#! /usr/bin/env python3

import re

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QDialog, QListWidget, QVBoxLayout, QHBoxLayout, QPushButton

from plugins_service.plugin_base import PluginBase

VOID_ELEMENTS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
}


class ValErrorsDialog(QDialog):
    def __init__(self, errors, editor, on_revalidate=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Validation errors')
        self.setMinimumSize(500, 100)
        self._editor = editor
        self._on_revalidate = on_revalidate

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget(self)
        for line_num, msg in errors:
            self.list_widget.addItem(f'Row {line_num}: {msg}')
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        revalidate_btn = QPushButton('Re-validate', self)
        close_btn = QPushButton('Close', self)
        btn_layout.addWidget(revalidate_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.list_widget.itemClicked.connect(self._on_item_clicked)
        revalidate_btn.clicked.connect(self._on_revalidate_clicked)
        close_btn.clicked.connect(self.close)

    def _on_revalidate_clicked(self):
        self.close()
        if self._on_revalidate:
            self._on_revalidate()

    def _on_item_clicked(self, item):
        text = item.text()
        match = re.match(r'Row (\d+):', text)
        if match:
            line = int(match.group(1))
            block = self._editor.document().findBlockByNumber(line - 1)
            if block:
                cursor = QTextCursor(block)
                self._editor.setTextCursor(cursor)
                self._editor.setFocus()


class HTMLProcessingPlugin(PluginBase):
    name = "htmlprocessing"
    description = "Обработка HTML кода в редакторе"
    message = pyqtSignal(str, str, str)

    actions = [
        {'id': "gen_content_list", 'text': "Generate content list",
         'callback': "gen_content_list"},
        {'id': "validate_html", 'text': "Validate HTML",
         'callback': "validate_html"},
    ]

    index_actions = {}
    for i in actions:
        i["kind"] = "action"
        index_actions[i['id']] = i

    menu_items = [
        {'kind': "menu", 'text': "Edit", 'content': [
            {'kind': "menu", 'text': "HTML", 'content': [
                index_actions['gen_content_list'],
                {'kind': "separator"},
                index_actions['validate_html'],
            ]}
        ]}
    ]

    def on_load(self, editor):
        self._editor = editor
        self.message.connect(editor.on_message)

    def on_unload(self):
        try:
            self.message.disconnect(self._editor.on_message)
        except TypeError:
            pass
        self._editor = None

    def gen_content_list(self, start_head_level=1, pass_nocontents=False):
        editor = self._editor.current_editor()
        if editor is None:
            return
        text = editor.toPlainText()

        heading_pattern = re.compile(
            r'<h([1-6])([^>]*)>(.*?)</h\1>', re.DOTALL | re.IGNORECASE
        )
        raw_headings = []
        for match in heading_pattern.finditer(text):
            level = int(match.group(1))
            attrs = match.group(2)
            heading_text = match.group(3)
            title = re.sub(r'<[^>]+>', '', heading_text).strip()
            if not title:
                continue
            pos = match.start()
            row_num = text[:pos].count('\n') + 1
            id_match = re.search(r'\bid\s*=\s*["\']([^"\']+)["\']', attrs)
            heading_id = id_match.group(1) if id_match else None
            nocontents = bool(
                re.search(r'\bclass\s*=\s*["\'].*?\bnocontents\b.*?["\']', attrs, re.DOTALL)
            )
            raw_headings.append({
                'level': level, 'title': title, 'id': heading_id,
                'row': row_num, 'nocontents': nocontents
            })

        if start_head_level > 1:
            raw_headings = [h for h in raw_headings if h['level'] >= start_head_level]

        if pass_nocontents:
            raw_headings = [h for h in raw_headings if not h['nocontents']]

        if not raw_headings:
            self._editor.msg_panel.new_view(
                "<i>No headings found in the document.</i>", 'html'
            )
            return

        for h in raw_headings:
            if h['id'] is None:
                self.message.emit(
                    f"header in the {h['row']} row has no anchor.",
                    self.__class__.__name__, 'info'
                )

        class Node:
            def __init__(self, level, heading_id=None, title=None):
                self.level = level
                self.heading_id = heading_id
                self.title = title
                self.children = []

        root = Node(0)
        stack = [root]

        for h in raw_headings:
            node = Node(h['level'], h['id'], h['title'])
            while stack and stack[-1].level >= h['level']:
                stack.pop()
            parent = stack[-1]
            while parent.level < h['level'] - 1:
                empty = Node(parent.level + 1)
                parent.children.append(empty)
                stack.append(empty)
                parent = empty
            parent.children.append(node)
            stack.append(node)

        def render(node, depth=0):
            indent = '\t' * depth
            parts = []
            if node.heading_id is not None:
                href = f'#{node.heading_id}' if node.heading_id else '#'
                if node.children:
                    parts.append(f'{indent}<li><a href="{href}">{node.title}</a>')
                    parts.append(f'{indent}\t<ul>')
                    for child in node.children:
                        parts.extend(render(child, depth + 2))
                    parts.append(f'{indent}\t</ul>')
                    parts.append(f'{indent}</li>')
                else:
                    parts.append(f'{indent}<li><a href="{href}">{node.title}</a></li>')
            else:
                parts.append(f'{indent}<ul>')
                for child in node.children:
                    parts.extend(render(child, depth + 1))
                parts.append(f'{indent}</ul>')
            return parts

        html_lines = ['<ul>']
        for child in root.children:
            html_lines.extend(render(child, 1))
        html_lines.append('</ul>')

        self._editor.msg_panel.new_view('\n'.join(html_lines))

    def validate_html(self):
        editor = self._editor.current_editor()
        if editor is None:
            return
        text = editor.toPlainText()
        fname = self._editor.current_file_name()

        clean = re.sub(r'<\?php[\s\S]*?\?>', '', text)
        clean = re.sub(r'<!--[\s\S]*?-->', '', clean)

        if not re.search(r'<[a-zA-Z/!]', clean):
            self.message.emit(
                f'File has no tags.', self.__class__.__name__, 'info'
            )
            return

        tag_pattern = re.compile(r'</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>')
        stack = []
        errors = []

        for match in tag_pattern.finditer(clean):
            full_tag = match.group(0)
            tag_name = match.group(1).lower()
            pos = match.start()
            line_num = clean[:pos].count('\n') + 1

            if full_tag.startswith('</'):
                if tag_name in VOID_ELEMENTS:
                    continue
                if not stack:
                    errors.append(
                        (line_num, f"Unexpected closing tag </{tag_name}>")
                    )
                    break
                open_tag, open_line = stack.pop()
                if open_tag != tag_name:
                    errors.append((
                        line_num,
                        f"Mismatched tag: </{tag_name}> does not "
                        f"match <{open_tag}> opened at line {open_line}"
                    ))
                    break
            elif full_tag.endswith('/>') or tag_name in VOID_ELEMENTS:
                continue
            else:
                stack.append((tag_name, line_num))

        if not errors and stack:
            tag_name, line_num = stack[0]
            errors.append((
                line_num,
                f"Unclosed tag <{tag_name}> opened at line {line_num}"
            ))

        if not errors:
            self.message.emit(
                f'No errors in {fname}.', self.__class__.__name__, 'info'
            )
        else:
            dialog = ValErrorsDialog(
                errors, editor, self.validate_html, self._editor
            )
            self._val_dialog = dialog
            dialog.show()
