#! /usr/bin/python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from pathlib import Path
import sys
import os

from lib.file_tab_panel import *
from lib.msg_panel import *
import libiclear.iclear as iclib
from libiclear.wiclear import WinNodesNav, IclearInputDialog
					
class MultiEditor(QMainWindow):
	
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)	 
		
		self.win_title = "MultiEditor"
		self.restoreSettings()
		
		self.recent_files = self.settings.value("recent_files", []) or []
		self.iclear_support = self.settings.value("iclear/support", None) or None

		self.setWindowTitle(self.win_title)
		self.setFont(QFont('SansSerif', int(self.settings.value("font_point_size", 12)) ))
		
		self.move(self.settings.value("geometry/pos", QPoint(100, 100)))
		self.resize(self.settings.value("geometry/size", QSize(1200, 800)))
		
		self.tab_panel = TabPanel(parent=self, editor=TextEditor)
		self.msg_panel = MsgPanel(parent=self)
		sys.stderr = StdErrHandler(self.msg_panel.err_box)
		
		self.splitter = QSplitter(Qt.Vertical)
		self.splitter.addWidget(self.tab_panel)
		self.splitter.addWidget(self.msg_panel)
		self.splitter.setSizes([500,100])
		self.setCentralWidget(self.splitter)

		self.create_menu_bar()
		self.create_status_bar()
		self.create_toolbar()
		
		self.set_tab_panel()
		
		self.tab_panel.tab_status_changed.connect(self.on_editor_tab_status_changed)
		self.tab_panel.new_status_msg.connect(self.set_status_bar_msg)
		self.tab_panel.file_opened_or_saved_as.connect(self.add_recent_file)
		self.tab_panel.editor_cursor_position_changed.connect(self.set_permanent_status_msg)
		
		self.on_editor_tab_status_changed()
		
		
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
		create_menu_action(file_menu, "Property", self.tab_panel.property_tab)
		file_menu.addSeparator()
		
		self.recent_files_menu = file_menu.addMenu("Recent files")
		self.create_recent_files_menu()

		file_menu.addSeparator()
		
		create_menu_action(file_menu, "Exit", self.close, shortcut="Ctrl+Q")

		# optional Text Menu 
		if hasattr(self.tab_panel.editor_class, 'text_actions'):
			text_menu = menu_bar.addMenu('Text')
			for action in self.tab_panel.editor_class.text_actions:
				create_menu_action(text_menu, action['name'], self.ext_action, data=action['act'])
				
				
		# Tool menu
		tool_menu = menu_bar.addMenu('Tool')
		
		create_menu_action(tool_menu, "Zoom In", self.zoom_in, shortcut=QKeySequence.ZoomIn)
		create_menu_action(tool_menu, "Zoom Out", self.zoom_out, shortcut=QKeySequence.ZoomOut)
		tool_menu.addSeparator()
		create_menu_action(tool_menu, "Turn Iclear support", self.turn_iclear_support)

	def ext_action(self):
		action = self.sender()
		method_name = action.data()
		getattr(self.tab_panel.get_current_editor().editor, method_name)()
		
	def turn_iclear_support(self):
		iclear_hostpath = self.settings.value("iclear/hostpath", '') or ''
		iclear_sitepath = self.settings.value("iclear/sitepath", '') or ''
		
		dialog = IclearInputDialog()
		if dialog.exec_() == QDialog.Accepted:
			hostpath, sitepath = dialog.get_values()
			#print(f"Значения из диалога: '{hostpath}', '{sitepath}'")
			if hostpath.strip() != '':
				path = Path(hostpath)
				if path.exists():
					self.iclear_support = True
					self.iclear_hostpath = hostpath.strip()
					self.iclear_sitepath = sitepath.strip()
			else:
				self.iclear_support = None
				
	def create_toolbar(self):
		if self.iclear_support:
			self.create_iclear_tool()
		
	def create_iclear_tool(self):
		self.iclear_hostpath = self.settings.value("iclear/hostpath", '') or ''
		self.iclear_sitepath = self.settings.value("iclear/sitepath", '') or ''
		
		host = iclib.IHost("iclear", self.iclear_hostpath, self.iclear_sitepath)
		host.fill(fill_sites = True, fill_mans = True)

		nodedict = {'site': self.settings.value("iclear/site", ""),
					'top': self.settings.value("iclear/top", ""),
					'man': self.settings.value("iclear/man", ""),
					"cat": self.settings.value("iclear/cat", ""),
					"page": self.settings.value("iclear/page", "")}
					
		nodnav = iclib.NodesNav(host = host, nodedict = nodedict)
		
		self.iclear_widget = WinNodesNav(nodnav, parent=self)
		
		iclear_tool_bar = QToolBar('iclear')
		self.addToolBar(iclear_tool_bar)
		iclear_tool_bar.addWidget(self.iclear_widget)
			
	def create_status_bar(self):
		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		self.status_msg_box = QLabel(parent=self)
		self.statusBar.addPermanentWidget(self.status_msg_box)
		self.statusBar.showMessage("Ready")
		
	def set_permanent_status_msg(self, msg):
		self.status_msg_box.setText(f"Строка: {msg}")	
		
	def on_editor_tab_status_changed(self):
		self. set_window_title()
		if self.iclear_support:
			self.set_iclear_widget()
		
	def set_window_title(self):
		""" self.tab_panel.tab_status_changed.connect(self.set_window_title) """
		current_editor = self.tab_panel.get_current_editor()
		if current_editor:
			path_name, full_path_name, mod_label = current_editor.get_info()
			self.setWindowTitle(f"{full_path_name + mod_label} - {self.win_title}")
		else:
			self.setWindowTitle(self.win_title)
		
	def set_iclear_widget(self):
		if self.iclear_support:
			current_editor = self.tab_panel.get_current_editor()
			if current_editor:
				path = current_editor.path
				if path:
					self.iclear_widget.fill_from_page_path(str(path))
					
	def set_status_bar_msg(self, msg):
		self.statusBar.showMessage(msg, 2000)	
			
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

	def saveSettings(self, open_files):
		font_point_size = self.font().pointSize()
		self.settings.setValue("geometry/size", self.size()) 
		self.settings.setValue("geometry/pos", self.pos())
		self.settings.setValue("font_point_size", font_point_size)
		self.settings.setValue("recent_files", self.recent_files)
		self.settings.setValue("open_files", open_files)
		if self.iclear_support:
			self.settings.setValue("iclear/support", self.iclear_support)
			self.settings.setValue("iclear/hostpath", self.iclear_hostpath)
			self.settings.setValue("iclear/sitepath", self.iclear_sitepath)
			self.settings.setValue("iclear/site", self.iclear_widget.nodnav.repr_node("site"))		
			self.settings.setValue("iclear/top", self.iclear_widget.nodnav.repr_node("top"))
			self.settings.setValue("iclear/man", self.iclear_widget.nodnav.repr_node("man"))
			self.settings.setValue("iclear/cat", self.iclear_widget.nodnav.repr_node("cat"))
			self.settings.setValue("iclear/page", self.iclear_widget.nodnav.repr_node("page"))
		
		self.settings.sync()
		
class StdErrHandler(QObject):
    
	def __init__(self, widget):
		self.widget = widget
		self.original_stderr = sys.stderr
		self.app = QApplication.instance() if (QApplication.instance() is not None) else QApplication(sys.argv)

	def write(self, message):
		# Выводим в оригинальную stderr (консоль)
		self.original_stderr.write(message)
		self.original_stderr.flush()
		self.widget.append(f"<span style='color: red;'>{message.strip()}</span>")
		self.app.beep()
		
	def flush(self):
		self.original_stderr.flush()
		
if __name__ == "__main__":
	
	import sys

	app = QApplication(sys.argv)
	multi_editor = MultiEditor()	
	multi_editor.setWindowIcon(QIcon('icons/clear.svg'))								 
	multi_editor.show()			
							 
	sys.exit(app.exec_()) 	
 
