#! /usr/bin/env python3

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTabWidget, QTextEdit, QFileDialog, QMessageBox

from pathlib import Path
import datetime
import os

from core.file_editor import FileEditor


class TabPanel(QTabWidget):
	
	tab_added = pyqtSignal(object)
	editor_state_changed = pyqtSignal(str, str, str, str)
	line_changed = pyqtSignal(int)
	message = pyqtSignal(str, str, str)

	def __init__(self, parent=None, editor_class=QTextEdit):
		super().__init__(parent)

		self.editor_class = editor_class

		self.setMovable(True)
		self.setTabsClosable(True)

		self.tabCloseRequested.connect(self.close_tab)
		self.do_not_process_the_tab_change = False
		self.currentChanged.connect(self.on_current_tab_changed)

	def get_current_editor(self):
		current_widget = self.currentWidget()
		if current_widget:
			return current_widget
		return None

	def get_current_path(self):
		current_widget = self.currentWidget()
		if current_widget:
			if current_widget.path:
				return str(current_widget.path)
		return ''

	def on_current_tab_changed(self, index):
		if self.do_not_process_the_tab_change:
			return
		current_editor = self.widget(index)
		if current_editor:
			current_editor.setFocus()
			path_name, full_path_name, mod_label = current_editor.get_info()
		else:
			path_name, full_path_name, mod_label = '', '', ''
		self.editor_state_changed.emit(path_name, full_path_name, mod_label, 'tab_changed')

	def on_user_modification_changed(self, name, fname, mod_label):
		index = self.currentIndex()
		self.set_tab_text_and_tooltip(name, fname, mod_label, index)
		self.editor_state_changed.emit(name, fname, mod_label, 'modification_changed')

	def set_tab_text_and_tooltip(self, name, fname, mod_label, index):
		if index is not None:
			self.setTabToolTip(index, fname)
			self.setTabText(index, f'{name}{mod_label}')

	def add_tab(self, path=None):
		if path:
			for i in range(self.count()):
				if self.widget(i).path == path:
					self.do_not_process_the_tab_change = True
					self.setCurrentIndex(i)
					self.do_not_process_the_tab_change = False
					fname = str(path)
					self.message.emit(f'file {fname} already open', self.__class__.__name__, 'info')
					mod_label = self.get_current_editor().get_modification_label()
					self.editor_state_changed.emit(path.name, fname, mod_label, 'Reopened')
					return True
			if not self.check_path_exists(path):
				return False

		file_editor = FileEditor(parent=self, path=path, editor_class=self.editor_class)

		file_editor.user_modification_changed.connect(self.on_user_modification_changed)
		file_editor.line_changed.connect(self.line_changed)
		file_editor.message.connect(self.message)

		path_name = file_editor.get_path_name()

		self.do_not_process_the_tab_change = True
		index = self.addTab(file_editor, path_name)
		self.setCurrentIndex(index)
		self.do_not_process_the_tab_change = False

		if path is not None:
			if not file_editor.load_from_file():
				return False
			operation = 'Opened'
		else:
			operation = 'New'

		name, fname = file_editor.get_path_name(), file_editor.get_full_path()
		self.set_tab_text_and_tooltip(name, fname, '', index)
		self.tab_added.emit(file_editor.editor)
		self.editor_state_changed.emit(name, fname, '', operation)
		return True

	def set_files(self, file_list):
		opened = 0
		for file_path in file_list:
			path = Path(file_path)
			if path.exists():
				if self.add_tab(path):
					opened += 1
		return opened

	def new_tab(self):
		self.add_tab(None)

	def open_file(self):
		file_path, _ = QFileDialog.getOpenFileName(
			self, "Open File", "", "Text Files (*.txt);;All Files (*)")
		if file_path == '':
			return
		self.add_tab(Path(file_path))

	def close_tab(self, index, close_last_tab = False):
		if (not close_last_tab) and (self.count() <= 1):
			return False

		file_editor = self.widget(index)
		if file_editor.isModified():
			path_name = file_editor.get_path_name()
			text_question = f'"{path_name}" has unsaved changes. Do you want to save before closing?'
			if file_editor.is_externally_modified():
				text_question += ' <span style="color:red">Attention! The file on the disk is newer than in the editor.</span>'
			reply = QMessageBox.question(
				self, 'Unsaved Changes', text_question,
				QMessageBox.Save | QMessageBox.Ignore | QMessageBox.Cancel)
			if reply == QMessageBox.Cancel:
				return False
			elif reply == QMessageBox.Save:
				if self.save_tab(index, file_editor):
					self.removeTab(index)
					return True
				else:
					return False

		self.removeTab(index)
		return True

	def close_all_tab(self):
		for i in reversed(range(self.count())):
			self.setCurrentIndex(i)
			if not self.close_tab(i, close_last_tab = True):
				return False
		return True

	def current_tab_close(self):
		index = self.currentIndex()
		return self.close_tab(index)

	def current_tab_save(self):
		index = self.currentIndex()
		if index == -1:
			return
		current_editor = self.get_current_editor()
		self.save_tab(index, current_editor)

	def current_tab_save_as(self):
		index = self.currentIndex()
		if index == -1:
			return
		current_editor = self.get_current_editor()
		self.save_as_tab(index, current_editor)

	def current_tab_reload(self):
		index = self.currentIndex()
		if index == -1:
			return
		current_editor = self.get_current_editor()
		self.reload_tab(index, current_editor)

	def save_tab(self, index, file_editor):
		path = file_editor.path
		if path is None:
			return self.save_as_tab(index, file_editor)
		if not self.check_path_exists(path):
			return False
		if file_editor.save_to_file():
			self.set_tab_text_and_tooltip(path.name, str(path), '', index)
			self.editor_state_changed.emit(path.name, str(path), '', 'Saved')
			return True

	def save_as_tab(self, index, file_editor):
		file_path = QFileDialog.getSaveFileName(self, "Save As", os.getcwd())[0]
		if file_path == '':
			return
		path = Path(file_path)
		if file_editor.save_as_file(path):
			self.set_tab_text_and_tooltip(path.name, file_path, '', index)
			self.editor_state_changed.emit(path.name, file_path, '', 'Saved as')
			return True

	def reload_tab(self, index, file_editor):
		path = file_editor.path
		if path is None:
			return False
		if not self.check_path_exists(path):
			return False
		cursor = file_editor.editor.textCursor()
		position = cursor.position()
		if file_editor.load_from_file():
			max_position = len(file_editor.editor.toPlainText())
			position = min(position, max_position)
			cursor.setPosition(position)
			file_editor.editor.setTextCursor(cursor)
			self.set_tab_text_and_tooltip(path.name, str(path), '', index)
			self.editor_state_changed.emit(path.name, str(path), '', 'Reload')
			return True
		else:
			return False

	def current_tab_view_property(self):
		current_editor = self.get_current_editor()
		if current_editor is None:
			return
		path = current_editor.path
		if not self.check_path_exists(path):
			return
		QMessageBox.information(self, "Property", str(path),
			buttons=QMessageBox.Close, defaultButton=QMessageBox.Close)

	def get_open_files(self):
		open_files = []
		for i in range(self.count()):
			path = self.widget(i).path
			if path:
				open_files.append(str(path))
		return open_files

	def closeEvent(self, event):
		if self.close_all_tab():
			event.accept()
		else:
			event.ignore()

	def check_path_exists(self, path):
		if not path.exists():
			QMessageBox.information(self, "no file", "There is no such file or directory",
					buttons=QMessageBox.Close, defaultButton=QMessageBox.Close)
			return False
		return True

	def on_app_focus_changed(self, old, now):
		index = self.currentIndex()
		if index == -1:
			return
		if getattr(self, 'on_app_focus_changed_temporarily_disabled', False):
			return
		current_editor = self.get_current_editor()
		if current_editor and current_editor.path:
			if now and isinstance(now, self.editor_class):
				self.on_app_focus_changed_temporarily_disabled = True
				self.check_tab_externally_modified(index, current_editor)
				self.on_app_focus_changed_temporarily_disabled = False

	def check_tab_externally_modified(self, index, file_editor):
		if file_editor.path is None:
			return False
		if not self.check_path_exists(file_editor.path):
			return False
		if file_editor.is_externally_modified():
			msg_box = QMessageBox(self)
			msg_box.setWindowTitle("External modification")
			msg_box.setText("The file on the disk is newer than in the editor. Select the required action:")
			reload_button = msg_box.addButton("Reload", QMessageBox.ActionRole)
			msg_box.setStandardButtons(QMessageBox.Save | QMessageBox.Ignore)
			msg_box.exec_()
			clicked = msg_box.clickedButton()
			if clicked == msg_box.button(QMessageBox.Save):
				return self.save_tab(index, file_editor)
			elif clicked == msg_box.button(QMessageBox.Ignore):
				file_editor.last_file_mtime = datetime.datetime.now()
				return
			elif clicked == reload_button:
				return self.reload_tab(index, file_editor)

	def current_editor(self) -> QTextEdit:
		widget = self.currentWidget()
		if hasattr(widget, 'editor'):
			return widget.editor
		return None
