#! /usr/bin/python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from pathlib import Path
import sys
import os
import datetime

if __name__ == '__main__':
	from editor_ext import *
else:
	from lib.editor_ext import *

def get_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app
 
class FileDocEditor(QTextEdit):
	
	doc_state_changed = pyqtSignal()
 
	def __init__(self, parent=None, path=None):
		super(FileDocEditor, self).__init__(parent)
		""" if  path == None - this is new file """
		self.path = path
		if path:
			self.load_from_file()
			self.last_file_mtime = datetime.datetime.now()
				
		self.textChanged.connect(self.current_doc_changed)
		self.doc_state_changed.connect(self.current_doc_changed)
		
	def load_from_file(self):
		""" load and reload  """
		file_content = self.path.read_text(encoding="utf-8")
		if file_content:
			self.setText(file_content)
			self.document().setModified(False)
			self.last_file_mtime = datetime.datetime.now()
			self.doc_state_changed.emit()
			return True
			
	def doc_path_name(self):
		return self.path.name if self.path else "untitled"
		
	def doc_full_path(self):
		return str(self.path) if self.path else "untitled"
		
	def doc_modification_label(self):
		return "*" if self.document().isModified() else ""
		
	def doc_info(self):
		return self.doc_path_name(), self.doc_full_path(), self.doc_modification_label()
			
	def current_doc_changed(self):
		self.last_file_mtime = datetime.datetime.now()
		
	def save_to_file(self):  
		"""Writing an existing file with old name"""
		if self.path.write_text(self.toPlainText()):
			self.document().setModified(False)
			self.doc_state_changed.emit()
			return True
			
	def save_as_file(self, path):  
		"""Writing a new file or a file with a new name"""
		self.path = path
		if self.save_to_file():
			self.doc_state_changed.emit()
			return True

	def externally_modified(self): 
		if self.path:
			stat = self.path.stat()
			file_mtime = stat.st_mtime
			file_datetime = datetime.datetime.fromtimestamp(file_mtime)
			return True if self.last_file_mtime < file_datetime else False
			
'''
class FileDocEditorExt(FileDocEditor, TextEditorExt):

	def __init__(self, parent=None, path=None):
		""" if  path == None - this is new file """
		super(FileDocEditorExt, self).__init__(parent)
'''

class DocTabPanel(QTabWidget): 
	""" Create tab widget for multiple documents """
	
	change_current_tab_status = pyqtSignal()
	new_status_msg = pyqtSignal(str)
	
	def __init__(self, parent=None, editor=FileDocEditor, detect_externally_modified=False):
		super(DocTabPanel, self).__init__(parent)
		
		self.EditorCls = editor
		self.detect_externally_modified = detect_externally_modified

		self.setTabsClosable(True)
		self.tabCloseRequested.connect(self.close_tab)
		self.currentChanged.connect(self.current_tab_changed)

		self.app = get_app()
		if self.detect_externally_modified:
			self.currentChanged.connect(self.set_focus_on_editor)
			self.app.focusChanged.connect(self.app_focus_changed)
		
	def get_current_editor(self):
		"""Return the current text editor widget or None """
		current_widget = self.currentWidget()
		if current_widget:
			return current_widget
		return None
		
	def current_tab_changed(self, index):
		""" whenever the current page index changes """
		self.change_current_tab_status.emit()
		
	def update_current_tab_title(self):
		""" called from editor -> editor.textChanged.connect(self.update_current_tab_title), 
		    selt.save_tab(), selt.save_as_tab """
		if self.count() == 0:
			return
		current_index = self.currentIndex()
		current_editor = self.get_current_editor()
		path_name, full_path_name, mod_label = current_editor.doc_info()
		self.setTabText(current_index, path_name + mod_label)  
		self.setTabToolTip(current_index, full_path_name)
		self.change_current_tab_status.emit()
			
	def add_tab(self, path: Path):
		""" if  path == None - this is new file """
		if path:
			# check if file already open
			for i in range(self.count()):
				if self.widget(i).path == path:
					self.setCurrentIndex(i)
					return
			if not self.check_path_exists(path):
				return False
			
		editor = self.EditorCls(parent=self, path=path)
		editor.textChanged.connect(self.update_current_tab_title)
		
		path_name = editor.doc_path_name()
		full_path_name = editor.doc_full_path()
		
		index = self.addTab(editor, path_name)
		self.setTabToolTip(index, full_path_name)
		self.setCurrentIndex(index)
		self.change_current_tab_status.emit()
		self.new_status_msg.emit(f"Opened {path_name}")
		return True
		
	def new_tab(self):
		self.add_tab(None)
		
	def save_tab(self):
		editor = self.get_current_editor()
		if editor is None:
			return
		path = editor.path
		if path is None:
			self.save_as_tab()
			return
 
		if editor.save_to_file():
			path_name = editor.doc_path_name()
			self.update_current_tab_title()  
			self.change_current_tab_status.emit()
			self.new_status_msg.emit(f"Saved {path_name}")
			return True
				
	def save_as_tab(self):
		editor = self.get_current_editor()
		if editor is None:
			return
		
		file_path = QFileDialog.getSaveFileName(self, "Save As", os.getcwd())[0]
		if file_path == '':
			self.win_main.update_status_bar("Cancelled", 2000)
			return 
			
		path = Path(file_path)
		if editor.save_as_file(path):
			path_name = editor.doc_path_name()
			self.update_current_tab_title()  
			self.change_current_tab_status.emit()
			self.new_status_msg.emit(f"Saved {path_name}")
			return True
			
	def reload_tab(self):
		current_editor = self.get_current_editor()
		if current_editor is None:
			return
		path = current_editor.path
		if path is None:
			return
		if current_editor.load_from_file():
			path_name = current_editor.doc_path_name()
			self.update_current_tab_title()  
			self.change_current_tab_status.emit()
			self.new_status_msg.emit(f"Reload {path_name}")
			return True
			
	def close_tab(self, index):
		""" self.tabCloseRequested.connect(self.close_tab) """
		editor = self.widget(index)
		if editor.document().isModified():
			self.check_current_tab_externally_modified(editor)
			path_name = editor.doc_path_name()
			reply = QMessageBox.question(
				self, 'Unsaved Changes',
				f'"{path_name}" has unsaved changes. Do you want to save before closing?',
				QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
			if reply == QMessageBox.Cancel:
				return False
			elif reply == QMessageBox.Yes:
				if self.save_tab():
					self.removeTab(index)
					self.change_current_tab_status.emit()
					return True
				else:
					return False
		'''if the text has not changed or Discard is pressed '''
		self.removeTab(index)
		self.change_current_tab_status.emit()
		return True
					
	def close_all_tab(self):
		# Close all tabs in the reverse order 
		for i in reversed(range(self.count())):
			self.setCurrentIndex(i)
			if not self.close_tab(i):
				return False
		return True
		
	def check_path_exists(self, path):
		if not path.exists():
			QMessageBox.information(self, "no file", "There is no such file or directory",
					buttons=QMessageBox.Close, defaultButton=QMessageBox.Close)
			return False
		else:
			return True
			
	def in_tab_remove_empty_lines(self):
		current_editor = self.get_current_editor()
		current_editor.remove_empty_lines_in_selected()
				
	def set_focus_on_editor(self):
		""" When displaying the main window or switching to it in the OS,
		 in some cases only the QTabBar gets the focus. """
		current_editor = self.get_current_editor()
		if current_editor and current_editor.path:
			current_editor.setFocus()
		
	def check_current_tab_externally_modified(self, editor):
		""" warning - if no file or file has been changed 
			self.currentChanged.connect(self.check_current_tab_externally_modified)	"""
		if not self.detect_externally_modified:
			return
		if editor.path:
			if not self.check_path_exists(editor.path):
				return False
		file_name = editor.doc_path_name()
		if editor.path:
			if editor.externally_modified():
				QMessageBox.warning(self, "file on the disk has been changed",
					f"The file {file_name} on the disk is newer than in the editor", 
					buttons=QMessageBox.Close, defaultButton=QMessageBox.Close)
				editor.last_file_mtime = datetime.datetime.now()

	def app_focus_changed(self, old, now):
		""" app.focusChanged.connect(self.app_focus_changed)  """
		current_editor = self.get_current_editor()
		if current_editor and current_editor.path:
			file_name = current_editor.doc_path_name()
			if now and now.__class__ == self.EditorCls:
				#print(f"focusChanged {file_name}")
				self.app.focusChanged.disconnect(self.app_focus_changed)
				self.check_current_tab_externally_modified(current_editor)
				self.app.focusChanged.connect(self.app_focus_changed)
				
class MainWin(QMainWindow):
	''' for debugging on run as main '''
	def __init__(self):
		super(QMainWindow, self).__init__()
		self.doc_tab_panel = DocTabPanel()
		self.setCentralWidget(self.doc_tab_panel)
		self.doc_tab_panel.new_tab()
		menu_bar = self.menuBar()
		file_menu = menu_bar.addMenu("File")
		file_menu.addAction('New', self.doc_tab_panel.new_tab)
		file_menu.addAction('Open', self.open_file)
		file_menu.addAction('Save', self.doc_tab_panel.save_tab)
		file_menu.addAction('Save As ', self.doc_tab_panel.save_as_tab)

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


