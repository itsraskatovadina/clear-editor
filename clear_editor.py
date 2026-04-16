#! /usr/bin/python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from pathlib import Path
import sys
import os
import datetime

class FileDocEditor(QTextEdit):
	
	doc_state_changed = pyqtSignal()
 
	def __init__(self, parent=None, path=None):
		super(FileDocEditor, self).__init__(parent)
		""" if  path == None - this is new file """
		self.path = path
		if path:
			self.load_from_file()
		self.last_change_time = datetime.datetime.now()
				
		self.textChanged.connect(self.current_doc_changed)
		self.doc_state_changed.connect(self.current_doc_changed)
		
	def load_from_file(self):
		file_content = self.path.read_text(encoding="utf-8")
		if file_content:
			self.setText(file_content)
			self.last_change_time = datetime.datetime.now()
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
		self.last_change_time = datetime.datetime.now()
		
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
			return True if self.last_change_time < file_datetime else False

class DocTabPanel(QTabWidget): 
	""" Create tab widget for multiple documents """
	
	change_current_tab_status = pyqtSignal()
	new_status_msg = pyqtSignal(str)
	
	def __init__(self, parent=None, editor=FileDocEditor, detect_externally_modified=False):
		super(DocTabPanel, self).__init__(parent)
		
		self.EditorCls = editor
		self.setTabsClosable(True)
		self.tabCloseRequested.connect(self.close_tab)
		self.currentChanged.connect(self.current_tab_changed)

		self.detect_externally_modified = detect_externally_modified
		if detect_externally_modified:
			self.currentChanged.connect(self.set_focus_on_editor)
			app.focusChanged.connect(self.app_focus_changed)
		
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
			self.new_status_msg.emit("Cancelled")
			return 
			
		path = Path(file_path)
		if editor.save_as_file(path):
			path_name = editor.doc_path_name()
			self.update_current_tab_title()  
			self.change_current_tab_status.emit()
			self.new_status_msg.emit(f"Saved {path_name}")
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
				editor.last_change_time = datetime.datetime.now()

	def app_focus_changed(self, old, now):
		""" app.focusChanged.connect(self.app_focus_changed)  """
		current_editor = self.get_current_editor()
		if current_editor and current_editor.path:
			file_name = current_editor.doc_path_name()
			if now and now.__class__ == self.EditorCls:
				#print(f"focusChanged {file_name}")
				app.focusChanged.disconnect(self.app_focus_changed)
				self.check_current_tab_externally_modified(current_editor)
				app.focusChanged.connect(self.app_focus_changed)
					
class MultiDocEditor(QMainWindow):
	def __init__(self):
		super(QMainWindow, self).__init__()

		self.init_ui()
		
	def init_ui(self):
		self.win_title = "MultiDoc Editor"
		self.win_font = QFont('SansSerif', 12)
		self.recent_files = []

		self.setWindowTitle(self.win_title)
		self.setFont(self.win_font)
		
		self.restoreSettings()
		self.move(self.settings.value("geometry/pos", QPoint(100, 100)))
		self.resize(self.settings.value("geometry/size", QSize(1200, 800)))
		
		self.doc_tab_panel = DocTabPanel(self, detect_externally_modified=True)

		self.create_menu_bar()
		self.create_status_bar()
		
		central_widget = QWidget()
		self.setCentralWidget(central_widget)
		layout = QVBoxLayout(central_widget)
		layout.addWidget(self.doc_tab_panel)
		
		self.doc_tab_panel.change_current_tab_status.connect(self.update_window_title)
		self.doc_tab_panel.new_status_msg.connect(self.update_status_bar)
		
		self.doc_tab_panel.new_tab()

	def create_menu_bar(self):
		menu_bar = self.menuBar()
		
		# File Menu
		file_menu = menu_bar.addMenu("File")
		
		new_file_action = file_menu.addAction("New")
		new_file_action.setShortcut("Ctrl+N")
		new_file_action.triggered.connect(self.new_file)

		open_file_action = file_menu.addAction("Open File")
		open_file_action.setShortcut("Ctrl+O")
		open_file_action.triggered.connect(self.open_file)

		file_menu.addSeparator()
		
		save_file_action = file_menu.addAction("Save")
		save_file_action.setShortcut("Ctrl+S")
		save_file_action.triggered.connect(self.save_file)

		save_as_action = file_menu.addAction("Save As")
		save_as_action.setShortcut("Ctrl+Shift+S")
		save_as_action.triggered.connect(self.save_as_file)
		
		self.recent_files_menu = file_menu.addMenu("Recent files")
		self.create_recent_files_menu()	 
		
		file_menu.addSeparator()
		
		exit_action = file_menu.addAction("Exit")
		exit_action.setShortcut(QKeySequence.Quit)
		exit_action.triggered.connect(self.close)
		
	def create_status_bar(self):
		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		self.statusBar.showMessage("Ready")
						
	def update_window_title(self):
		""" the current tab has been changed by the user (click or move), 
			setCurrentIndex, setCurrentWidget """
		current_editor = self.doc_tab_panel.get_current_editor()
		if current_editor:
			path_name, full_path_name, mod_label = current_editor.doc_info()
			self.setWindowTitle(f"{full_path_name + mod_label} - {self.win_title}")
		else:
			self.setWindowTitle(self.win_title)
					
	def update_status_bar(self, msg):
		self.statusBar.showMessage(msg, 2000)	
 
	def open_file(self):
		# open file
		file_path, _ = QFileDialog.getOpenFileName(
			self, "Open File", "", "Text Files (*.txt);;All Files (*)")
		if file_path == '':
			self.update_status_bar("Cancelled")
			return
			
		self.doc_tab_panel.add_tab(Path(file_path))
		self.add_recent_file(file_path)
		
	def new_file(self):
		self.doc_tab_panel.new_tab()
		
	def save_as_file(self):
		self.doc_tab_panel.save_as_tab()
				
	def save_file(self):
		self.doc_tab_panel.save_tab()
					
	def closeEvent(self, event):
		"""Handle application close event"""
		if self.doc_tab_panel.close_all_tab():
			self.saveSettings()
			event.accept()
		else:
			event.ignore()
		
	def open_recent_file(self):
		action = self.sender()
		path = action.data()
		if not Path(path).exists():
			QMessageBox.information(self, "no file", "There is no such file or directory",
					buttons=QMessageBox.Close, defaultButton=QMessageBox.Close)
			return
		if path:
			self.doc_tab_panel.add_tab(Path(path))
			self.add_recent_file(path)
		
	def create_recent_files_menu(self):
		self.recent_files_menu.clear() 
 
		for i, file_path in enumerate(self.recent_files):
			action_text = f"{i+1}. {file_path}"
			action = QAction(action_text, self)
			action.setData(file_path)
			action.triggered.connect(self.open_recent_file)
			self.recent_files_menu.addAction(action)
			
		if not self.recent_files:
			no_files_action = QAction("No recent file", self)
			no_files_action.setEnabled(False)
			self.recent_files_menu.addAction(no_files_action)
			
	def add_recent_file(self, full_path):
		if full_path in self.recent_files:
			self.recent_files.remove(full_path)
		self.recent_files.insert(0, full_path)
		if len(self.recent_files) > 10:
			self.recent_files = self.recent_files[:10]
		self.create_recent_files_menu()
		
	def restoreSettings(self):	
		self.settings = QSettings(Path(sys.argv[0]).stem+".ini", QSettings.IniFormat)
		self.recent_files = self.settings.value("recent_files", []) or []
		
	def saveSettings(self):	
		self.settings.setValue("geometry/size", self.size()) 
		self.settings.setValue("geometry/pos", self.pos())
		self.settings.setValue("recent_files", self.recent_files)
		self.settings.sync()
		
if __name__ == '__main__':
	app = QApplication([])
	win = MultiDocEditor()
	win.setWindowIcon(QIcon('icons/clear.svg'))
	win.show()
	sys.exit(app.exec())
