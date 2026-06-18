#! /usr/bin/env python3

from PyQt5.QtGui import QTextCursor

from plugins_service.plugin_base import PluginBase


class TextProcessingPlugin(PluginBase):
	name = "textprocessing"
	description = "Обработка текста в редакторе"

	menu_items = {
		"Text": [
			{"text": "Remove empty lines", "callback": "remove_empty_lines_in_selected"},
			{"text": "Capitalize first letters", "callback": "capitalize_first_letters_in_selected"},
		]
	}

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
