#! /usr/bin/env python3

from PyQt5.QtGui import QTextCursor

from plugins_service.plugin_base import PluginBase


class TextProcessingPlugin(PluginBase):
    name = "textprocessing"
    description = "Обработка текста в редакторе"

    actions = [
        {'id': "remove_empty", 'text': "Remove empty lines",
         'callback': "remove_empty_lines_in_selected"},
        {'id': "capitalize_first", 'text': "Capitalize first letters",
         'callback': "capitalize_first_letters_in_selected"},
        {'id': "replace_entity", 'text': "Replace entity",
         'callback': "replace_entity_in_selected"},
        {'id': "wrap_p", 'text': "Wrap <p>", 'short_text': "<p>",
         'callback': "wrap_p_in_selected"},
        {'id': "wrap_b", 'text': "Wrap <b>", 'short_text': "<b>",
         'callback': "wrap_b_in_selected"},
        {'id': "unwrap", 'text': "Unwrap",
         'callback': "unwrap_in_selected"},
        {'id': "make_list", 'text': "Make list", 'short_text': "<ul>",
         'callback': "make_list_in_selected"},
        {'id': "make_nested_list", 'text': "Nested list", 'short_text': "<ul+>",
         'callback': "make_nested_list_in_selected"},
        {'id': "make_table", 'text': "Make table",
         'callback': "make_table_in_selected"},
    ]

    index_actions = {}
    for i in actions:
        i["kind"] = "action"
        index_actions[i['id']] = i

    menu_items = [
        {'kind': "menu", 'text': "Edit", 'content': [
            index_actions['remove_empty'],
            index_actions['capitalize_first'],
            {'kind': "separator"},
            {'kind': "menu", 'text': "HTML", 'content': [
                index_actions['wrap_p'],
                index_actions['wrap_b'],
                index_actions['unwrap'],
                index_actions['make_list'],
                index_actions['make_nested_list'],
                index_actions['make_table']
            ]}
            ]
        }]

    toolbar_items = [
        {**index_actions['wrap_p'], 'text': index_actions['wrap_p']['short_text']},
        {**index_actions['wrap_b'], 'text': index_actions['wrap_b']['short_text']},
        {**index_actions['make_list'], 'text': index_actions['make_list']['short_text']},
        {**index_actions['make_nested_list'], 'text': index_actions['make_nested_list']['short_text']},
    ]

    def on_load(self, editor):
        self._panel = editor.tab_panel

    def on_unload(self):
        self._panel = None

    def selectedTextProcessing(self, func, **kwargs):
        editor_widget = self._panel.currentWidget().editor
        cursor = editor_widget.textCursor()
        if not cursor.hasSelection():
            return False

        selected_text = cursor.selectedText().replace("\u2029", "\n")
        out_text = func(selected_text, **kwargs)
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(out_text)
        cursor.endEditBlock()

        cursor.setPosition(cursor.position() - len(out_text))
        cursor.setPosition(cursor.position() + len(out_text), QTextCursor.MoveMode.KeepAnchor)
        editor_widget.setTextCursor(cursor)
        return True

    def remove_empty_lines_in_selected(self):
        self.selectedTextProcessing(
            lambda text: "\n".join(line for line in text.split("\n") if line.strip())
        )

    def capitalize_first_letters_in_selected(self):
        self.selectedTextProcessing(
            lambda text: "\n".join(
                line[0].upper() + line[1:] if line else line
                for line in text.split("\n")
            )
        )

    def replace_entity_in_selected(self):
        self.selectedTextProcessing(
            lambda text: text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )

    def wrap_p_in_selected(self):
        self.selectedTextProcessing(
            lambda text: "\n".join(
                f"<p>{line}</p>" if line.strip() else line
                for line in text.split("\n")
            )
        )

    def wrap_b_in_selected(self):
        self.selectedTextProcessing(
            lambda text: f"<b>{text}</b>"
        )

    def unwrap_in_selected(self):
        def unwrap(text):
            text = text.strip()
            if not text.startswith("<"):
                return text
            end_open = text.find(">")
            if end_open == -1:
                return text
            tag_name = text[1:end_open].split()[0]
            closing = f"</{tag_name}>"
            if text.endswith(closing):
                return text[end_open + 1:-len(closing)]
            return text
        self.selectedTextProcessing(unwrap)

    def make_list_in_selected(self):
        def to_list(text):
            items = [line.strip() for line in text.split("\n") if line.strip()]
            if not items:
                return text
            lis = "\n".join(f"    <li>{item}</li>" for item in items)
            return f"<ul>\n{lis}\n</ul>"
        self.selectedTextProcessing(to_list)

    @staticmethod
    def _indent_depth(raw):
        normalized = raw.replace('\t', '    ')
        return len(normalized) // 4

    def make_nested_list_in_selected(self):
        def to_nested_list(text):
            lines = [line for line in text.split('\n') if line.strip()]
            if not lines:
                return text

            root_children = []
            stack = []
            for line in lines:
                stripped = line.lstrip()
                raw = line[:len(line) - len(stripped)]
                depth = TextProcessingPlugin._indent_depth(raw)
                node = [stripped, []]
                while stack and stack[-1][0] >= depth:
                    stack.pop()
                if stack:
                    stack[-1][1].append(node)
                else:
                    root_children.append(node)
                stack.append((depth, node[1]))

            def render(children, depth):
                out = []
                indent = '\t' * depth
                for text, grandchildren in children:
                    if grandchildren:
                        out.append(f'{indent}<li>{text}\t<ul>')
                        out.extend(render(grandchildren, depth + 1))
                        out.append(f'{indent}</ul></li>')
                    else:
                        out.append(f'{indent}<li>{text}</li>')
                return out

            result = ['<ul>']
            result.extend(render(root_children, 1))
            result.append('</ul>')
            return '\n'.join(result)
        self.selectedTextProcessing(to_nested_list)

    def make_table_in_selected(self):
        def to_table(text):
            rows = [line.strip() for line in text.split("\n") if line.strip()]
            if not rows:
                return text
            trs = []
            for row in rows:
                cells = row.split("\t")
                tds = "\n".join(f"            <td>{cell}</td>" for cell in cells)
                trs.append(f"        <tr>\n{tds}\n        </tr>")
            body = "\n".join(trs)
            return f"<table>\n{body}\n    </table>"
        self.selectedTextProcessing(to_table)
