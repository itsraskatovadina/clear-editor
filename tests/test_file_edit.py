#! /usr/bin/env python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon

from pathlib import Path
import sys
import datetime

from core.file_editor import FileEditor

class Editor_Win(QMainWindow):
	def __init__(self, parent=None, editor_class=QTextEdit):
		super(QMainWindow, self).__init__()

		self.editor_class = editor_class
		self.file_editor = FileEditor(self, editor_class=editor_class)

		self.setWindowTitle('FileEditor')
		central_widget = QWidget(self)
		self.setCentralWidget(central_widget)
		layout = QVBoxLayout(central_widget)
		self.file_name = QLabel(self)
		layout.addWidget(self.file_name)
		layout.addWidget(self.file_editor)

		self.file_editor.line_changed.connect(self.on_line_changed)
		self.file_editor.user_modification_changed.connect(self.on_user_modification_changed)
		self.file_editor.message.connect(self.on_message)
		
		self.create_menu_bar()
		self.create_status_bar()

		self.on_line_changed(self.file_editor.editor.textCursor().blockNumber() + 1)
		self.file_editor.emit_user_modification_changed()

	def set_file_names(self, name, fname, mod_label):
		self.setWindowTitle(f'{mod_label}{fname} - FileEditor')
		self.file_name.setText(f'File name: {name}')

	def on_user_modification_changed(self, name, fname, mod_label):
		self.set_file_names(name, fname, mod_label)

	def on_line_changed(self, line_num):
		self.cursor_line.setText(f'Line: {str(line_num)}')

	def on_message(self, msg, sender=None, msgtype=None):
		print(msg, sender, msgtype)
		
	def create_menu_bar(self):
		menu_bar = self.menuBar()
		file_menu = menu_bar.addMenu("File")
		file_menu.addAction('Open', self.open_file)
		file_menu.addAction('Save', self.save_file)
		file_menu.addAction('Save As', self.save_as_file)

	def create_status_bar(self):
		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		self.cursor_line = QLabel(parent=self)
		self.statusBar.addPermanentWidget(self.cursor_line)
		self.statusBar.showMessage("Ready")

	def on_status_bar_message(self, msg):
		self.statusBar.showMessage(f'{msg}', 2000)

	def open_file(self):
		file_path, _ = QFileDialog.getOpenFileName(
			self, "Open File", '', "Text Files (*.txt);;All Files (*)")
		if file_path == '':
			return
		self.file_editor.path = Path(file_path)
		self.file_editor.load_from_file()
		self.set_file_names(self.file_editor.path.name, file_path, '')
		if self.file_editor.isModified():
			print('Error self.file_editor.isModified() = True')

	def save_file(self):
		if self.file_editor.path is None:
			return self.save_as_file()
		self.file_editor.save_to_file()
		self.set_file_names(self.file_editor.path.name, str(self.file_editor.path), '')
		if self.file_editor.isModified():
			print('Error self.file_editor.isModified() = True')

	def save_as_file(self):
		file_path = QFileDialog.getSaveFileName(self, "Save As")[0]
		if file_path == '':
			return
		self.file_editor.save_as_file(Path(file_path))
		self.set_file_names(self.file_editor.path.name, file_path, '')

	def on_app_focus_changed(self, old, now):
		if getattr(self, 'on_app_focus_changed_temporarily_disabled', False):
			return
		if self.file_editor.path:
			if now and now.__class__ == self.editor_class:
				self.on_app_focus_changed_temporarily_disabled = True
				if self.file_editor.is_externally_modified():
					QMessageBox.information(self, "externally_modified", "file is externally modified",
						buttons=QMessageBox.Close, defaultButton=QMessageBox.Close)
					self.file_editor.last_file_mtime = datetime.datetime.now()
				self.on_app_focus_changed_temporarily_disabled = False

if __name__ == "__main__":
	app = QApplication(sys.argv)

	win = Editor_Win()
	app.focusChanged.connect(win.on_app_focus_changed)
	
	win.setWindowIcon(QIcon('icons/clear_test.jpg'))
	win.show()
	sys.exit(app.exec())
