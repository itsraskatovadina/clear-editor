#! /usr/bin/python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from pathlib import Path
import sys
import os

from lib.file_tab_panel import *
					
class MultiEditor(QMainWindow):
	
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)	 
		
		self.win_title = "MultiEditor"
		self.recent_files = []

		self.restoreSettings()
		
		self.setWindowTitle(self.win_title)
		self.setFont(QFont('SansSerif', int(self.settings.value("font_point_size", 12)) ))
		
		self.move(self.settings.value("geometry/pos", QPoint(100, 100)))
		self.resize(self.settings.value("geometry/size", QSize(1200, 800)))
		
		self.tab_panel = TabPanel(parent=self, editor=TextEditor)
		self.setCentralWidget(self.tab_panel)

		self.create_menu_bar()
		self.create_status_bar()
		
		self.tab_panel.tab_status_changed.connect(self.set_window_title)
		self.tab_panel.new_status_msg.connect(self.update_status_bar)
		self.tab_panel.file_opened_or_saved_as.connect(self.add_recent_file)
		
		self.set_tab_panel()

	def set_tab_panel(self):
		
		open_files = self.settings.value("open_files", []) or []
		if (open_files) and (len(open_files)>0):
			for file_path in open_files:
				self.tab_panel.add_tab(Path(file_path)) 
		if (self.tab_panel.count()==0):
			self.tab_panel.new_tab()
			
	def create_menu_bar(self):
			
		def create_menu_action(menu, name, connection,
				icon=None, shortcut=None, statustip=None, data=None):
			action = menu.addAction(name)
			action.triggered.connect(connection)
			if icon: action.setIcon(icon)
			if shortcut: action.setShortcut(shortcut)
			if statustip: action.setStatusTip(statustip)
			if data: action.setData(data)
			return action
		
		menu_bar = self.menuBar()
		
		# File Menu
		file_menu = menu_bar.addMenu("File")

		create_menu_action(file_menu, "New", self.tab_panel.new_tab, shortcut="Ctrl+N")
		create_menu_action(file_menu, "Open", self.tab_panel.open_file, shortcut="Ctrl+O", statustip="Open File")
		create_menu_action(file_menu, "Save", self.tab_panel.save_tab, shortcut="Ctrl+S")
		create_menu_action(file_menu, "Save As", self.tab_panel.save_as_tab, shortcut="Ctrl+Shift+S")
		create_menu_action(file_menu, "Reload", self.tab_panel.reload_tab, shortcut="Ctrl+Shift+R")
		
		file_menu.addSeparator()
		
		self.recent_files_menu = file_menu.addMenu("Recent files")
		self.create_recent_files_menu()

		file_menu.addSeparator()
		
		create_menu_action(file_menu, "Exit", self.close, shortcut="Ctrl+Q")
 
		if hasattr(self.tab_panel.editor_class, 'text_actions'):
			# Text menu
			text_menu = menu_bar.addMenu('Text')
			for action in self.tab_panel.editor_class.text_actions:
				create_menu_action(text_menu, action['name'], self.ext_action, data=action['act'])
				
				
		# Tool menu
		tool_menu = menu_bar.addMenu('Tool')
		
		create_menu_action(tool_menu, "Zoom In", self.zoom_in, shortcut=QKeySequence.ZoomIn)
		create_menu_action(tool_menu, "Zoom Out", self.zoom_out, shortcut=QKeySequence.ZoomOut)
		tool_menu.addSeparator()
		create_menu_action(tool_menu, "Turn IclearLib", self.turn_iclear_lib)

	def ext_action(self):
		action = self.sender()
		method_name = action.data()
		getattr(self.tab_panel.get_current_editor().editor, method_name)()
		
	def turn_iclear_lib(self):
		pass
		
	def create_status_bar(self):
		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		self.statusBar.showMessage("Ready")
		
	def set_window_title(self):
		""" self.tab_panel.tab_status_changed.connect(self.set_window_title) """
		current_editor = self.tab_panel.get_current_editor()
		if current_editor:
			path_name, full_path_name, mod_label = current_editor.get_info()
			self.setWindowTitle(f"{full_path_name + mod_label} - {self.win_title}")
		else:
			self.setWindowTitle(self.win_title)
					
	def update_status_bar(self, msg):
		self.statusBar.showMessage(msg, 2000)	
		
	'''
	def action_open_file(self):
		self.tab_panel.open_file()
	def action_save_file(self):
		self.tab_panel.save_tab()
	def action_save_as_file(self):
		self.tab_panel.save_as_tab()
	def action_reload_file(self):
		self.tab_panel.reload_tab()
	'''
			
	def action_open_recent_file(self):
		action = self.sender()
		full_path = action.data()
		path = Path(full_path)
		self.tab_panel.add_tab(path)
			
	def action_clear_recent_files(self):
		self.recent_files = []
		self.create_recent_files_menu()
			
	def create_recent_files_menu(self):
		self.recent_files_menu.clear() 
		
		for i, file_path in enumerate(self.recent_files):
			action_text = f"{i+1}. {file_path}"
			action = QAction(action_text, self)
			action.setData(file_path)
			action.triggered.connect(self.action_open_recent_file)
			self.recent_files_menu.addAction(action)
			
		if (not self.recent_files) or (len(self.recent_files)==0):
			no_files_action = QAction("No recent file", self)
			no_files_action.setEnabled(False)
			self.recent_files_menu.addAction(no_files_action)
		elif len(self.recent_files)>0:
			self.recent_files_menu.addSeparator()
			action = self.recent_files_menu.addAction("Clear recent files")
			action.triggered.connect(self.action_clear_recent_files)
			
	def add_recent_file(self, full_path):
		if full_path in self.recent_files:
			self.recent_files.remove(full_path)
		self.recent_files.insert(0, full_path)
		if len(self.recent_files) > 10:
			self.recent_files = self.recent_files[:10]
		self.create_recent_files_menu()
			
	def closeEvent(self, event):
		open_files = self.tab_panel.get_open_files()
		if self.tab_panel.close_all_tab():
			self.saveSettings(open_files)
			event.accept()
		else:
			event.ignore()	
		
	def zoom_in(self):
		"""Zoom in (increase font size)"""
		font = self.font()
		font.setPointSize(font.pointSize() + 1)
		self.setFont(font)

	def zoom_out(self):
		"""Zoom out (decrease font size)"""
		font = self.font()
		font.setPointSize(max(6, font.pointSize() - 1))
		self.setFont(font)
			
	def restoreSettings(self):	
		self.settings = QSettings(Path(sys.argv[0]).stem+".ini", QSettings.IniFormat)
		self.recent_files = self.settings.value("recent_files", []) or []

	def saveSettings(self, open_files):
		font_point_size = self.font().pointSize()
		self.settings.setValue("geometry/size", self.size()) 
		self.settings.setValue("geometry/pos", self.pos())
		self.settings.setValue("font_point_size", font_point_size)
		self.settings.setValue("recent_files", self.recent_files)
		self.settings.setValue("open_files", open_files)
		self.settings.sync()
		
if __name__ == "__main__":
	
	import sys

	app = QApplication(sys.argv)
	multi_editor = MultiEditor()	
	multi_editor.setWindowIcon(QIcon('icons/clear.svg'))								 
	multi_editor.show()										 
	sys.exit(app.exec_()) 	
 
