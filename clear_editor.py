#! /usr/bin/python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from pathlib import Path
import sys
import os

from lib.file_tab_editor import *
					
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
		#self.doc_tab_panel = DocTabPanel(self, editor=FileDocEditorExt, detect_externally_modified=True)
		self.create_menu_bar()
		#self.create_menu_bar_ext()
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

		save_as_action = file_menu.addAction("Reload")
		save_as_action.setShortcut("Ctrl+Shift+R")
		save_as_action.triggered.connect(self.doc_tab_panel.reload_tab)
		
		file_menu.addSeparator()
		
		self.recent_files_menu = file_menu.addMenu("Recent files")
		self.create_recent_files_menu()	 
		
		file_menu.addSeparator()
		
		exit_action = file_menu.addAction("Exit")
		exit_action.setShortcut(QKeySequence.Quit)
		exit_action.triggered.connect(self.close)
		
	def create_menu_bar_ext(self):
		menu_bar = self.menuBar()
		
		ext_menu = menu_bar.addMenu("Ext")
		ext_menu.addAction('Remove empty lines', self.doc_tab_panel.in_tab_remove_empty_lines)
		
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
	app = QApplication(sys.argv)
	win = MultiDocEditor()
	win.setWindowIcon(QIcon('icons/clear.svg'))
	win.show()
	sys.exit(app.exec())
