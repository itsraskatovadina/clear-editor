#! /usr/bin/python3

from PyQt5.QtWidgets import QTextEdit, QInputDialog, QApplication
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QSyntaxHighlighter, QTextCursor, QTextCharFormat, QColor, QFont
    
from lib.editorlib import EditLib

class HtmlHighlighter(QSyntaxHighlighter):

	tag_format = QTextCharFormat()
	tag_format.setForeground(QColor("blue"))
	tag_format.setFontWeight(QFont.Bold)
	quote_format = QTextCharFormat()
	quote_format.setForeground(QColor("green"))
	comment_format = QTextCharFormat()
	comment_format.setForeground(QColor("red"))

	tag_pattern = QRegularExpression(r"<[^>]+>")
	quote_pattern = QRegularExpression(r"'[^']*'")
	double_quote_pattern = QRegularExpression(r'"[^"]*"')
	comment_pattern = QRegularExpression(r"<!--(?:[^-]|-(?!-))*-->")
		
	def __init__(self, parent=None):
		super().__init__(parent)
		self.highlighting_rules = []
		self.highlighting_rules.append((HtmlHighlighter.tag_pattern, HtmlHighlighter.tag_format))
		self.highlighting_rules.append((HtmlHighlighter.quote_pattern, HtmlHighlighter.quote_format))
		self.highlighting_rules.append((HtmlHighlighter.double_quote_pattern, HtmlHighlighter.quote_format))
		self.highlighting_rules.append((HtmlHighlighter.comment_pattern, HtmlHighlighter.comment_format))
		
	def highlightBlock(self, text):
		for pattern, format in self.highlighting_rules:
			match_iter = pattern.globalMatch(text)
			while match_iter.hasNext():
				match = match_iter.next()
				self.setFormat(match.capturedStart(), match.capturedLength(), format)

class TextEditor(QTextEdit):

	actions = [
		{'action': "remove_empty_lines_in_selected", 'name': "Remove empty lines"},
		{'action': "capitalize_first_letters_in_selected", 'name': "Capitalize first letters"}
	]
	
	index_actions = {}
	for i in actions: index_actions[i['action']] = i
	
	class_actions = [
		{'action': "menu", 'name': "Text", 'content': [
			index_actions['remove_empty_lines_in_selected'],
			index_actions['capitalize_first_letters_in_selected']
		]}
	]
	
	def __init__(self, parent=None):
		super().__init__(parent)
		
	def selectedTextProcessing(self, func, **kwargs):
		''' processing selected text '''
		cursor = self.textCursor()
		if not cursor.hasSelection():
			return False
		selected_text = cursor.selectedText().replace("\u2029", "\n")
		out_text = func(selected_text, **kwargs)
		cursor.beginEditBlock()
		cursor.removeSelectedText()
		cursor.insertText(out_text)
		cursor.endEditBlock()
		# selecting the processed text
		cursor.setPosition(cursor.position() - len(out_text))
		cursor.setPosition(cursor.position() + len(out_text), 
						  QTextCursor.MoveMode.KeepAnchor)
		self.setTextCursor(cursor)
					
	def remove_empty_lines_in_selected(self):
		''' remove the empty lines in the selected block  '''
		self.selectedTextProcessing(EditLib.remove_empty_lines)
		
	def capitalize_first_letters_in_selected(self):
		''' capitalize the first letters in the selected block '''
		self.selectedTextProcessing(EditLib.capital_first_letter)

class HTMLEditor(TextEditor):

	actions = TextEditor.actions.copy()
	actions.extend([
		{'action': "replace_entity", 'name': "Replace entity"},
		{'action': "wrap_p", 'name': "Wrap <p>", 'icon': 'icons/tagp.png', 'tooltip': "Wrap &lt;p&gt;", 'statustip': "Wrap selected <p>...</p>"},
		{'action': "wrap_b", 'name': "Wrap <b>", 'icon': 'icons/tagb.png'},
		{'action': "wrap_div", 'name': "Wrap <div>"},               
		{'action': "select_tag_to_wrap", 'name': "Select tag to wrap"},
		{'action': "wrap_selected_tag", 'name': "Wrap selected tag"},
		{'action': "make_list", 'name': "ul", 'tooltip': "Make list"}
	])

	index_actions = {}
	for i in actions: index_actions[i['action']] = i
	
	class_actions = TextEditor.class_actions.copy()
	class_actions.extend([
		{'action': "menu", 'name': "HTML", 'content': [
			index_actions['replace_entity'],
			{'action': "menu", 'name': "Wrap", 'content': [
				index_actions['wrap_p'],
				index_actions['wrap_b'],
				index_actions['wrap_div'],
				index_actions['select_tag_to_wrap'],
				index_actions['wrap_selected_tag']
			]},
			index_actions['make_list']
		]},
		{'action': "tool", 'name': "HTML", 'content': [
			index_actions['wrap_p'],
			index_actions['wrap_b'],
			index_actions['make_list']
		]}
	])
	
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.highlighter = HtmlHighlighter(self.document())
		self.autocompletion_tags = ['p', 'b', 'div', 'span', 'a', 'ul', 'li',
			'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'tr', 'td']
		self.tag_to_wrap = 'span'

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
		''' replaces the html entity in the selected fragment '''
		self.selectedTextProcessing(EditLib.replace_entity)

	def wrap_p(self):
		self.selectedTextProcessing(EditLib.wrap, tag='p')

	def wrap_b(self):
		self.selectedTextProcessing(EditLib.wrap, tag='b')
		
	def wrap_div(self):
		self.selectedTextProcessing(EditLib.wrap, tag='div')
		
	def select_tag_to_wrap(self):
		'''  to be implemented  '''
		s, ok = QInputDialog.getItem(self, "Select tag",
			f"Select the tag for the wrap operation,<br> the '{self.tag_to_wrap}' tag is currently selected",
			 self.autocompletion_tags[3:], current=1, editable=False)
		if ok:
			self.tag_to_wrap = s
		
	def wrap_selected_tag(self):
		self.selectedTextProcessing(EditLib.wrap, tag=self.tag_to_wrap)
		
	def make_list(self):
		''' generates a list of non-empty lines in the selected fragment '''
		self.selectedTextProcessing(EditLib.make_list)
