#! /usr/bin/env python3

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QTextEdit, QHBoxLayout

from pathlib import Path
import datetime


class FileEditor(QWidget):
	untitled_name = "untitled"
	modification_label = "*"

	user_modification_changed = pyqtSignal(str, str, str)
	line_changed = pyqtSignal(int)
	message = pyqtSignal(str, str, str)

	def __init__(self, parent=None, editor_class=QTextEdit, path=None):
		super().__init__(parent)

		self.editor = editor_class(parent=self)

		hbox = QHBoxLayout()
		hbox.setContentsMargins(0, 0, 0, 0)
		hbox.addWidget(self.editor)
		self.setLayout(hbox)

		self.is_programmatic_modification_change = False

		self.editor.document().modificationChanged.connect(self.on_editor_modification_changed)
		self.editor.cursorPositionChanged.connect(self.on_cursor_position_changed)

		self.path = path
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
		if not self.is_programmatic_modification_change:
			self.emit_user_modification_changed()

	def on_cursor_position_changed(self):
		line_num = self.editor.textCursor().blockNumber() + 1
		self.line_changed.emit(line_num)

	def load_from_file(self):
		try:
			file_content = self.path.read_text(encoding="utf-8")
			self.is_programmatic_modification_change = True
			self.editor.setPlainText(file_content)
			self.is_programmatic_modification_change = False
			self.last_file_mtime = datetime.datetime.now()
			return True
		except Exception as err:
			self.message.emit(str(err), self.__class__.__name__, 'error')
			return False

	def save_to_file(self):
		try:
			self.path.write_text(self.editor.toPlainText())
			self.last_file_mtime = datetime.datetime.now()
			self.is_programmatic_modification_change = True
			self.setModified(False)
			self.is_programmatic_modification_change = False
			return True
		except Exception as err:
			self.message.emit(str(err), self.__class__.__name__, 'error')
			return False

	def save_as_file(self, path):
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
