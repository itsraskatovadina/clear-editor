#! /usr/bin/python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
    
class TextEditorExt(QTextEdit):
	''' Text editor '''
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
		self.selectedTextProcessing(self.remove_empty_lines)
		
	def remove_empty_lines(self, txt):
		lines = txt.split('\n')
		non_empty_lines = []
		for line in lines:
			if line:	
				non_empty_lines.append(line)
		return '\n'.join(non_empty_lines)
		
