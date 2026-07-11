#! /usr/bin/env python3

import re

from PyQt5.QtGui import QTextCursor

from plugins_service.plugin_base import PluginBase


class TextProcessingPlugin(PluginBase):
    name = "textprocessing"
    description = "Обработка текста в редакторе"

    actions = [
        {
            "id": "remove_empty",
            "text": "Remove empty lines",
            "tooltip": "Delete all empty lines in selection",
            "statustip": "Delete all empty lines in selection",
            "callback": "remove_empty_lines_in_selected",
        },
        {
            "id": "capitalize_first",
            "text": "Capitalize first letters",
            "tooltip": "Capitalize the first letter of each line",
            "statustip": "Capitalize the first letter of each line",
            "callback": "capitalize_first_letters_in_selected",
        },
        {
            "id": "replace_entity",
            "text": "Replace entity",
            "tooltip": "Replace & < > with HTML entities",
            "statustip": "Replace & < > with HTML entities",
            "callback": "replace_entity_in_selected",
        },
        {
            "id": "wrap_p",
            "text": "Wrap <p>",
            "short_text": "<p>",
            "tooltip": "Wrap each line in <p> tags",
            "statustip": "Wrap each line in <p> tags",
            "callback": "wrap_p_in_selected",
        },
        {
            "id": "wrap_b",
            "text": "Wrap <b>",
            "short_text": "<b>",
            "tooltip": "Wrap selection in <b> tags",
            "statustip": "Wrap selection in <b> tags",
            "callback": "wrap_b_in_selected",
        },
        {
            "id": "unwrap",
            "text": "Unwrap",
            "tooltip": "Remove the outer HTML tag from selection",
            "statustip": "Remove the outer HTML tag from selection",
            "callback": "unwrap_in_selected",
        },
        {
            "id": "make_list",
            "text": "Make list",
            "short_text": "<ul>",
            "tooltip": "Convert lines to <ul><li> list",
            "statustip": "Convert lines to <ul><li> list",
            "callback": "make_list_in_selected",
        },
        {
            "id": "make_nested_list",
            "text": "Nested list",
            "short_text": "<ul+>",
            "tooltip": "Convert indented lines to nested <ul> list",
            "statustip": "Convert indented lines to nested <ul> list",
            "callback": "make_nested_list_in_selected",
        },
        {
            "id": "make_table",
            "text": "Make table",
            "tooltip": "Convert tab-separated text to <table>",
            "statustip": "Convert tab-separated text to <table>",
            "callback": "make_table_in_selected",
        },
        {
            "id": "compact_table",
            "text": "Compact table",
            "tooltip": "Compact HTML table: one <tr> per line, add <tbody>",
            "statustip": "Compact HTML table: one <tr> per line, add <tbody>",
            "callback": "compact_html_table_in_selected",
        },
    ]

    index_actions = {}
    for i in actions:
        i["kind"] = "action"
        index_actions[i["id"]] = i

    menu_items = [
        {
            "kind": "menu",
            "text": "Edit",
            "content": [
                index_actions["remove_empty"],
                index_actions["capitalize_first"],
                {"kind": "separator"},
                index_actions["wrap_p"],
                index_actions["wrap_b"],
                index_actions["unwrap"],
                {"kind": "separator"},
                index_actions["make_list"],
                index_actions["make_nested_list"],
                index_actions["make_table"],
                index_actions["compact_table"],
            ],
        }
    ]

    toolbar_items = [
        {**index_actions["wrap_p"], "text": index_actions["wrap_p"]["short_text"]},
        {**index_actions["wrap_b"], "text": index_actions["wrap_b"]["short_text"]},
        {
            **index_actions["make_list"],
            "text": index_actions["make_list"]["short_text"],
        },
        {
            **index_actions["make_nested_list"],
            "text": index_actions["make_nested_list"]["short_text"],
        },
    ]

    def on_load(self, editor):
        self._editor = editor

    def on_unload(self):
        self._editor = None

    def selectedTextProcessing(self, func, **kwargs):
        editor_widget = self._editor.current_editor()
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
        cursor.setPosition(
            cursor.position() + len(out_text), QTextCursor.MoveMode.KeepAnchor
        )
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
            lambda text: (
                text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
        )

    def wrap_p_in_selected(self):
        self.selectedTextProcessing(
            lambda text: "\n".join(
                f"<p>{line}</p>" if line.strip() else line for line in text.split("\n")
            )
        )

    def wrap_b_in_selected(self):
        self.selectedTextProcessing(lambda text: f"<b>{text}</b>")

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
                return text[end_open + 1 : -len(closing)]
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
        normalized = raw.replace("\t", "    ")
        return len(normalized) // 4

    def make_nested_list_in_selected(self):
        def to_nested_list(text):
            lines = [line for line in text.split("\n") if line.strip()]
            if not lines:
                return text

            root_children = []
            stack = []
            for line in lines:
                stripped = line.lstrip()
                raw = line[: len(line) - len(stripped)]
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
                indent = "\t" * depth
                for text, grandchildren in children:
                    if grandchildren:
                        out.append(f"{indent}<li>{text}\t<ul>")
                        out.extend(render(grandchildren, depth + 1))
                        out.append(f"{indent}</ul></li>")
                    else:
                        out.append(f"{indent}<li>{text}</li>")
                return out

            result = ["<ul>"]
            result.extend(render(root_children, 1))
            result.append("</ul>")
            return "\n".join(result)

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

    def compact_html_table_in_selected(self):
        def compact(text):
            if not re.search(r"<table[\s>]", text, re.IGNORECASE):
                raise ValueError("Selection does not contain a <table> tag")
            if not re.search(r"</table>", text, re.IGNORECASE):
                raise ValueError("Selection is missing </table> tag")

            rows = re.findall(r"<tr[\s>].*?</tr>", text, re.IGNORECASE | re.DOTALL)
            if not rows:
                raise ValueError("No <tr> rows found in table")

            compacted_rows = []
            for row in rows:
                one_line = re.sub(r"\s+", " ", row.strip())
                one_line = re.sub(r">\s+<", "><", one_line)
                compacted_rows.append(one_line)

            body = "\n".join(compacted_rows)
            return f"<table><tbody>\n{body}\n</tbody></table>"

        editor_widget = self._editor.current_editor()
        cursor = editor_widget.textCursor()
        if not cursor.hasSelection():
            return

        selected_text = cursor.selectedText().replace("\u2029", "\n")
        try:
            out_text = compact(selected_text)
        except ValueError as e:
            self._editor.msg_srv.post_message(
                str(e), "TextProcessing", "error"
            )
            return

        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(out_text)
        cursor.endEditBlock()

        cursor.setPosition(cursor.position() - len(out_text))
        cursor.setPosition(
            cursor.position() + len(out_text), QTextCursor.MoveMode.KeepAnchor
        )
        editor_widget.setTextCursor(cursor)
