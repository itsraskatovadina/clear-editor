#! /usr/bin/python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from pathlib import Path
import datetime

from lib.text_editor import *
	
class FileEditor(QWidget):
	
	html_extensions = ["html", "htm", "php"]
	untitled_name = "untitled"
	status_changed = pyqtSignal()  
	modification_changed = pyqtSignal(bool)
	cursor_position_changed = pyqtSignal(int)
	
	''' path: None | Path '''
	def __init__(self, parent=None, editor=QTextEdit, path=None):
		super(FileEditor, self).__init__(parent)
		
		self.editor = editor(parent=self)
		hbox = QHBoxLayout()	
		hbox.setContentsMargins(0,0,0,0)
		hbox.addWidget(self.editor)		
		self.setLayout(hbox)	
		self.editor.document().modificationChanged.connect(self.on_editor_modification_changed)
		self.editor.cursorPositionChanged.connect(self.on_cursor_position_changed)

		self.modified = False
		self.path = path
		if self.path:
			self.load_from_file()

	def on_editor_modification_changed(self, flag):
		self.modified = flag
		self.status_changed.emit()

	def isModified(self):
		return self.modified

	def on_cursor_position_changed(self):
		line_num = self.editor.textCursor().blockNumber() + 1
		self.cursor_position_changed.emit(line_num)

	def get_modification_label(self):
		return "*" if self.modified else ""
		
	def get_path_name(self):
		return self.path.name if self.path else FileEditor.untitled_name
		
	def get_full_path(self):
		return str(self.path) if self.path else FileEditor.untitled_name
		
	def get_info(self):
		return self.get_path_name(), self.get_full_path(), self.get_modification_label()
		
	def load_from_file(self):
		file_content = self.path.read_text(encoding="utf-8")
		if file_content:
			suffix = self.path.suffix[1:]
			if suffix in FileEditor.html_extensions:
				self.editor.setPlainText(file_content)
			else:
				self.editor.setText(file_content)
			self.last_file_mtime = datetime.datetime.now()
			self.status_changed.emit()
			return True
			
	def save_to_file(self):  
		"""Writing an existing file with old name"""
		if self.path.write_text(self.editor.toPlainText()):
			self.last_file_mtime = datetime.datetime.now()
			self.set_doc_modified_without_notification(False)
			self.status_changed.emit()
			return True
			
	def save_as_file(self, path):  
		"""Writing a new file or a file with a new name"""
		self.path = path
		return self.save_to_file()
			
	def set_doc_modified_without_notification(self, flag):
		self.editor.document().modificationChanged.disconnect(self.on_editor_modification_changed)
		self.editor.document().setModified(flag)
		self.modified = flag
		self.editor.document().modificationChanged.connect(self.on_editor_modification_changed)
		
		
	def is_externally_modified(self): 
		if self.path:
			stat = self.path.stat()
			file_mtime = stat.st_mtime
			file_datetime = datetime.datetime.fromtimestamp(file_mtime)
			return True if self.last_file_mtime < file_datetime else False
			
	def closeEvent(self, event):
		event.accept()
