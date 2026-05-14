#! /usr/bin/python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
    
from lib.editorlib import EditLib

class HtmlHighlighter(QSyntaxHighlighter):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.highlighting_rules = []

		# Формат для тегов
		tag_format = QTextCharFormat()
		tag_format.setForeground(QColor("green"))
		
		# Регулярное выражение для <...>
		pattern = QRegularExpression(r"<[^>]+>")
		self.highlighting_rules.append((pattern, tag_format))

	def highlightBlock(self, text):
		for pattern, format in self.highlighting_rules:
			match_iter = pattern.globalMatch(text)
			while match_iter.hasNext():
				match = match_iter.next()
				self.setFormat(match.capturedStart(), match.capturedLength(), format)

class TextEditor(QTextEdit):

	text_actions = []
	text_actions.append({'action': "remove_empty_lines_in_selected", 'name': "Remove empty lines"})
	text_actions.append({'action': "capitalize_first_letters_in_selected", 'name': "Capitalize first letters"})
	
	def __init__(self, parent=None):
		super().__init__(parent)
		
	def selectedTextProcessing(self, func):
		''' processing selected text '''
		cursor = self.textCursor()
		if cursor.hasSelection():
			selected_text = cursor.selectedText().replace("\u2029", "\n")
			# replace it, put it in the clipboard, paste it into the selected area
			# done via Copy/Paste so that there is only one action left in the Undo/Redo history.
			outtxt = func(selected_text)
			clipboard = QApplication.clipboard()
			clipboard.setText(outtxt)
			self.paste()
					
	def remove_empty_lines_in_selected(self):
		''' remove the empty lines in the selected block  '''
		self.selectedTextProcessing(EditLib.remove_empty_lines)
		
	def capitalize_first_letters_in_selected(self):
		''' capitalize the first letters in the selected block '''
		self.selectedTextProcessing(EditLib.capital_first_letter)

class HTMLEditor(TextEditor):

	html_actions = [
		{'action': "replace_entity", 'name': "Replace entity"},
		{'action': "menu", 'name': "Wrap", 'action_list': [
			{'action': "wrap", 'name': "Wrap <p>"},
			{'action': "wrap_b", 'name': "Wrap <b>"},
			{'action': "wrap_div", 'name': "Wrap <div>"},               
			{'action': "select_tag_to_wrap", 'name': "Select tag to wrap"}
			]},
		{'action': "make_list", 'name': "Make list"}
		]

	html_tools = [
		{'action': "wrap", 'name': "Wrap <p>", 'icon': 'icons/tagp.png', 'tooltip': "Wrap &lt;p&gt;", 'statustip': "Wrap selected <p>...</p>"},
		{'action': "wrap_b", 'name': "Wrap <b>", 'icon': 'icons/tagb.png'}]
	
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.highlighter = HtmlHighlighter(self.document())
		self.autocompletion_tags = ['p', 'b', 'div', 'span', 'a', 'ul', 'li',
			'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'tr', 'td']

	def keyPressEvent(self, event):
		#auto-completion of tags — intercepting the input '>' is a sign of tag closure
		if event.key() == Qt.Key_Greater and self.hasFocus():
			cursor = self.textCursor()
			text = self.toPlainText()

			pos = cursor.position()
			before = text[:pos]
			# looking for the last '<' before the cursor
			last_lt = before.rfind('<')
			if last_lt == -1:
				super().keyPressEvent(event)
				return

			# highlight the tag name (between '<' and '>')
			tag_candidate = before[last_lt + 1:pos].strip()
			if not tag_candidate or tag_candidate.startswith('/'):
				super().keyPressEvent(event)
				return

			# check that this is a known tag
			if tag_candidate in self.autocompletion_tags:
				# insert the '>' and close the tag
				cursor.insertText('>')
				closing_tag = f'</{tag_candidate}>'
				cursor.insertText(closing_tag)
				# moving the cursor in front of the closing tag (so that the user can write inside)
				cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(closing_tag))
				self.setTextCursor(cursor)
				return

		# for all other keys, this is the standard behavior.
		super().keyPressEvent(event)

	def replace_entity(self):
		''' в выделенном фрагменте заменяет html entity '''
		self.selectedTextProcessing(EditLib.replace_entity)

	def wrap(self, tag = 'p'):
		''' оборачивает выделенный фрагмент '''
		cursor = self.textCursor()
		if cursor.hasSelection():
			selected_text = cursor.selectedText().replace("\u2029", "\n")
			# оборачиваем, помещаем в буфер обмена, вставляем
			wrapped_text = EditLib.wrap(selected_text, tag)
			clipboard = QApplication.clipboard()
			clipboard.setText(wrapped_text)
			self.paste()

	def wrap_b(self):
		self.wrap('b')

	def wrap_div(self):
		self.wrap('div')
		
	def select_tag_to_wrap(self):
		pass
		
	def make_list(self):
		''' в выделенном фрагменте формирует список из не пустых строк '''
		self.selectedTextProcessing(EditLib.make_list)
