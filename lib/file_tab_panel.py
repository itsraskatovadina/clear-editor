#! /usr/bin/python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from pathlib import Path
import os

if __name__ == "__main__":
	from file_editor import *
else:
	from lib.file_editor import *

class TabPanel(QTabWidget):
	""" Tab widget for multiple documents """

	tab_status_changed = pyqtSignal()
	file_opened_or_saved_as = pyqtSignal(str)
	editor_cursor_position_changed = pyqtSignal(int)
	new_status_msg = pyqtSignal(str)

	def __init__(self, parent=None, editor=QTextEdit):
		super(TabPanel, self).__init__(parent)
		
		self.setMovable(True)
		self.setTabsClosable(True)
		self.tabCloseRequested.connect(self.close_tab)
		self.currentChanged.connect(self.on_current_tab_changed)

		self.editor_class = editor 
		
		self.app = QApplication.instance() if (QApplication.instance() is not None) else QApplication(sys.argv)
		self.app.focusChanged.connect(self.on_app_focus_changed)
		
	def get_current_editor(self):
		"""Return the current text editor widget or None """
		current_widget = self.currentWidget()
		if current_widget:
			return current_widget
		return None
		
	def on_current_tab_changed(self, index):
		""" self.currentChanged.connect(self.on_current_tab_changed)
			(the current tab can be changed by the user (by clicking or moving) 
			or from the program when calling setCurrentIndex, setCurrentWidget )
			in self.add_tab - self.setCurrentIndex(index)
			in main window -
			multi_editor.tab_panel.tab_status_changed.connect(self.set_window_title)   
			"""
		current_editor = self.widget(index) 
		if current_editor:
			current_editor.setFocus()
		self.tab_status_changed.emit()
		
	def on_tab_status_changed(self):
		""" in self.add_tab - editor.status_changed.connect(self.on_tab_status_changed)
			in main window -
			multi_editor.tab_panel.tab_status_changed.connect(self.set_window_title)   
			"""
		if self.count() > 0:
			current_index = self.currentIndex()
			self.set_tab_text_and_tooltip(current_index)
		self.tab_status_changed.emit()
		
	def set_tab_text_and_tooltip(self, index):
		current_editor = self.widget(index) 
		path_name, full_path_name, mod_label = current_editor.get_info()
		self.setTabText(index, path_name + mod_label)  
		self.setTabToolTip(index, full_path_name)
		return path_name, full_path_name, mod_label

	def add_tab(self, path):
		""" if  path == None - this is new file 
		call  when the user opens, open recent file, or opens saved tabs."""
		if path:
			# check if file already open
			for i in range(self.count()):
				if self.widget(i).path == path:
					self.setCurrentIndex(i)
					return
			if not path.exists():
				path = None
			else:
				self.file_opened_or_saved_as.emit(str(path))
				
		editor = FileEditor(parent=self, path=path, editor=self.editor_class)
		editor.status_changed.connect(self.on_tab_status_changed)
		editor.cursor_position_changed.connect(self.editor_cursor_position_changed)
		path_name = editor.get_path_name()
		index = self.addTab(editor, path_name)
		self.setCurrentIndex(index)
		path_name, full_path_name, mod_label = self.set_tab_text_and_tooltip(index)
		self.new_status_msg.emit(f"Opened {path_name}")
		return True
		
	def new_tab(self):
		self.add_tab(None)
		
	def open_file(self):
		# open file
		file_path, _ = QFileDialog.getOpenFileName(
			self, "Open File", "", "Text Files (*.txt);;All Files (*)")
		if file_path == '':
			return
		self.add_tab(Path(file_path))
		
	def save_tab(self):
		# save file
		current_editor = self.get_current_editor()
		if current_editor is None:
			return
		path = current_editor.path
		if path is None:
			return self.save_as_tab(current_editor)
		if not self.check_path_exists(path):
			return
		if current_editor.save_to_file():
			current_index = self.currentIndex()
			path_name, full_path_name, mod_label = self.set_tab_text_and_tooltip(current_index)
			self.tab_status_changed.emit()
			self.new_status_msg.emit(f"Saved {path_name}")
			return True
			
	def save_as_tab(self, editor):
		# save as file
		current_editor = self.get_current_editor()
		if current_editor is None:
			return
		file_path = QFileDialog.getSaveFileName(self, "Save As", os.getcwd())[0]
		if file_path == '':
			return 		
		if current_editor.save_as_file(Path(file_path)):
			current_index = self.currentIndex()
			path_name, full_path_name, mod_label = self.set_tab_text_and_tooltip(current_index)
			self.tab_status_changed.emit()
			self.file_opened_or_saved_as.emit(file_path)
			self.new_status_msg.emit(f"Saved as {path_name}")
			return True
			
	def reload_tab(self, editor):
		current_editor = self.get_current_editor()
		if current_editor is None:
			return
		path = current_editor.path
		if not self.check_path_exists(path):
			return
		if editor.load_from_file():
			current_index = self.currentIndex()
			path_name, full_path_name, mod_label = self.set_tab_text_and_tooltip(current_index)
			self.tab_status_changed.emit()
			self.new_status_msg.emit(f"Reload {path_name}")
			return True

	def close_tab(self, index):
		""" self.tabCloseRequested.connect(self.close_tab) """
		editor = self.widget(index)
		if editor.modified:
			if editor.path:
				self.check_tab_externally_modified(editor)
			path_name = editor.get_path_name()
			reply = QMessageBox.question(
				self, 'Unsaved Changes',
				f'"{path_name}" has unsaved changes. Do you want to save before closing?',
				QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
			if reply == QMessageBox.Cancel:
				return False
			elif reply == QMessageBox.Save:
				if self.save_tab():
					self.removeTab(index)
					return True
				else:
					return False
		'''if the text has not changed or Discard is pressed '''
		self.removeTab(index)
		self.tab_status_changed.emit()
		return True
		
	def close_all_tab(self):
		# Close all tabs in the reverse order 
		for i in reversed(range(self.count())):
			self.setCurrentIndex(i)
			if not self.close_tab(i):
				return False
		return True

	def get_open_files(self):
		open_files = []
		for i in range(self.count()):
			path = self.widget(i).path
			if path:
				open_files.append(str(path)) 
		return open_files

	def closeEvent(self, event):
		event.accept()
		
	def check_path_exists(self, path):
		if not path.exists():
			QMessageBox.information(self, "no file", "There is no such file or directory",
					buttons=QMessageBox.Close, defaultButton=QMessageBox.Close)
			return False
		else:
			return True	
			
	def on_app_focus_changed(self, old, now):
		""" app.focusChanged.connect(self.on_app_focus_changed)  """
		current_editor = self.get_current_editor()
		if current_editor and current_editor.path:
			file_name = current_editor.get_path_name()
			if now and now.__class__ == self.editor_class:
				self.app.focusChanged.disconnect(self.on_app_focus_changed)
				self.check_tab_externally_modified(current_editor)
				self.app.focusChanged.connect(self.on_app_focus_changed)
			
	def check_tab_externally_modified(self, editor):
		""" warning - if no file or file has been changed 
			self.currentChanged.connect(self.check_current_tab_externally_modified)	"""
		if editor.path is None:
			return False
		if not self.check_path_exists(editor.path):
			return False
		full_path = editor.get_full_path()
		if editor.is_externally_modified():
			QMessageBox.warning(self, "file on the disk has been changed",
				f"The file {full_path} on the disk is newer than in the editor", 
				buttons=QMessageBox.Close, defaultButton=QMessageBox.Close)
			editor.last_file_mtime = datetime.datetime.now()
		
		
class MainWin(QMainWindow):
	''' for debugging on run as main '''
	def __init__(self):
		super(QMainWindow, self).__init__()
		self.tab_panel = TabPanel()
		self.setCentralWidget(self.tab_panel)
		self.tab_panel.new_tab()
		menu_bar = self.menuBar()
		file_menu = menu_bar.addMenu("File")
		file_menu.addAction('New', self.tab_panel.new_tab)
		file_menu.addAction('Open', self.tab_panel.open_file)
		file_menu.addAction('Save', self.tab_panel.save_tab)
		file_menu.addAction('Save As ', self.tab_panel.save_as_tab)

	def open_file(self):
		# open file
		file_path, _ = QFileDialog.getOpenFileName(
			win, "Open File", "", "Text Files (*.txt);;All Files (*)")
		if file_path == '':
			return
		win.doc_tab_panel.add_tab(Path(file_path))
	
	def closeEvent(self, event):
		"""Handle application close event"""
		if self.doc_tab_panel.close_all_tab():
			event.accept()
		else:
			event.ignore()
    			
if __name__ == '__main__':

	app = QApplication(sys.argv)
	win = MainWin()	
	win.show()
	sys.exit(app.exec())


