#! /usr/bin/python3

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QMainWindow, QTextEdit,
                             QLabel, QStatusBar, QMessageBox, QFileDialog, QApplication)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon

from pathlib import Path
import datetime

from lib.text_editor import HTMLEditor

class FileEditor(QWidget):
	''' A wrapper over a custom editor '''
	
	# name for new (unsaved) files
	untitled_name = "untitled"
	# marker of the modified file
	modification_label = "*"

	# signal is emited when user modification changed a document, if the attribute is_programmatic_modification_change == False
	# signal parameters - file name, file full path, modification label(*)
	user_modification_changed = pyqtSignal(str, str, str)  
	# signal cursor_position_changed parameter - line number.
	cursor_position_changed = pyqtSignal(int)
	# signal parameters - message text, message_type = 'debug'/'info'/'warning'/'error'
	new_message = pyqtSignal(str, str)
	
	def __init__(self, parent=None, editor_class=QTextEdit, path=None):
		''' constructor accepts parent, editor_class (default QTextEdit), path (None | Path) '''
	
		super(FileEditor, self).__init__(parent)
				
		self.editor = editor_class(parent=self)
		hbox = QHBoxLayout()	
		hbox.setContentsMargins(0, 0, 0, 0)
		hbox.addWidget(self.editor)		
		self.setLayout(hbox)
		
		# a sign of programmatic modification of the document
		self.is_programmatic_modification_change = False
		
		self.editor.document().modificationChanged.connect(self.on_editor_modification_changed)
		self.editor.cursorPositionChanged.connect(self.on_cursor_position_changed)
		
		# the path to the document file, or None for the new file
		self.path = path
		# the time of the last program modification of the file
		self.last_file_mtime = datetime.datetime.now()

	def isModified(self):
		return self.editor.document().isModified()

	def setModified(self, flag):
		self.editor.document().setModified(flag)

	def get_modification_label(self):
		return FileEditor.modification_label if self.isModified() else ''
		
	def get_path_name(self):
		return self.path.name if self.path else FileEditor.untitled_name
		
	def get_full_path(self):
		return str(self.path) if self.path else FileEditor.untitled_name
		
	def get_info(self):
		return self.get_path_name(), self.get_full_path(), self.get_modification_label()
		
	def emit_user_modification_changed(self):
		name, fname, mod_label = self.get_info()
		self.user_modification_changed.emit(name, fname, mod_label)
		
	def on_editor_modification_changed(self, flag):
		# emit a signal only if the document is changed by the user
		if not self.is_programmatic_modification_change:
			self.emit_user_modification_changed()

	def on_cursor_position_changed(self):
		line_num = self.editor.textCursor().blockNumber() + 1
		self.cursor_position_changed.emit(line_num)

	def load_from_file(self):
		''' Reading a file from disk, loading content into the editor.
			Sets the modification flag programmatically to avoid triggering
			user modification signals. Updates last_file_mtime on success.
			On error, emits an error message via new_message signal and returns False.'''
		try:
			file_content = self.path.read_text(encoding="utf-8")
			self.is_programmatic_modification_change = True
			self.editor.setPlainText(file_content) 
			self.is_programmatic_modification_change = False
			self.last_file_mtime = datetime.datetime.now()
			return True
		except Exception as err:
			self.new_message.emit(str(err), 'error')
			return False
			
	def save_to_file(self):  
		''' Writing an existing file to disk.
			Sets the modification flag to False programmatically to avoid triggering
			user modification signals. Updates last_file_mtime on success.
			On error, emits an error message via new_message signal and returns False.'''
		try:
			self.path.write_text(self.editor.toPlainText())
			self.last_file_mtime = datetime.datetime.now()
			self.is_programmatic_modification_change = True
			self.setModified(False)
			self.is_programmatic_modification_change = False
			return True
		except Exception as err:
			self.new_message.emit(str(err), 'error')
			return False
			
	def save_as_file(self, path):  
		"""Writing a new file or a file with a new name"""
		self.path = path
		return self.save_to_file()
		
	def is_externally_modified(self): 
		if self.path:
			if self.path.exists():
				stat = self.path.stat()
				file_mtime = stat.st_mtime
				file_datetime = datetime.datetime.fromtimestamp(file_mtime)
				return True if self.last_file_mtime < file_datetime else False
		return False
