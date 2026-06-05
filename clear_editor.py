#! /usr/bin/python3

from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QSplitter, QStatusBar,
                             QLabel, QAction, QApplication, QDialog)
from PyQt5.QtCore import (Qt, QPoint, QSize, QSettings, pyqtSignal)
from PyQt5.QtGui import (QFont, QIcon, QKeySequence)

from pathlib import Path
import sys
import os
import importlib.util

from lib.file_tab_panel import *
from lib.msg_panel import *
					
class ClearEditor(QMainWindow):
	
	new_message = pyqtSignal(str, str)
	new_error = pyqtSignal(str)

	def __init__(self, parent = None, editor_class=QTextEdit):
		QMainWindow.__init__(self, parent)	 

		self.editor_class = editor_class
		self.win_title = "ClearEditor"
		self.restoreSettings()

		self.setWindowTitle(self.win_title)
		self.setFont(QFont('SansSerif', int(self.settings.value("font_point_size", 12)) ))
		self.move(self.settings.value("geometry/pos", QPoint(100, 100)))
		self.resize(self.settings.value("geometry/size", QSize(1200, 800)))
		
		self.tab_panel = TabPanel(parent=self, editor_class=editor_class) 
		self.msg_panel = MsgPanel(parent=self)
		
		self.splitter = QSplitter(Qt.Vertical)
		self.splitter.addWidget(self.tab_panel)
		self.splitter.addWidget(self.msg_panel)
		self.splitter.setSizes([500,100])
		self.setCentralWidget(self.splitter)

		# обработка сообщений и ошибок
		# signal parameters - message text, message_type = 'debug'/'info'/'warning'/'error'
		self.new_message.connect(self.msg_panel.new_message)
		self.new_error.connect(self.msg_panel.new_error)
		
		self.create_menu_bar()
		self.create_status_bar()
		self.create_toolbar()
		
		self.tab_panel.editor_state_changed.connect(self.on_editor_state_changed)
		self.tab_panel.editor_cursor_position_changed.connect(self.set_permanent_status_msg)
		self.tab_panel.new_message.connect(self.on_message)
		
		self.extensions = []
		self.load_extensions()
		
		self.set_tab_panel()

		app.focusChanged.connect(self.tab_panel.on_app_focus_changed)
		
	def load_extensions(self):
		# для установки clear nav
		# self.ic_create_iclear_tool()
		
		self.create_action(self.extensions_menu, "Toggle Iclear module", self.toggle_iclear_extension)
		iclear_support = self.settings.value("extensions/iclear", 0)
		if iclear_support == '1': 
			from extensions.iclear.iclear_extension import IClearExtension
			iclear = IClearExtension()
			
			widget = iclear.create_widget()
			self.iclear_toolbar = self.addToolBar('iclear')
			self.iclear_toolbar.addWidget(self.iclear_widget)
			'''
			self.tab_panel.currentChanged.connect(
				lambda: self.iclear_widget.fill_from_page_path(self.tab_panel.get_current_path()))
			'''
			self.extensions.append(iclear)
			
	def toggle_iclear_extension(self):
		
		iclear = None
		for extension in self.extensions:
			if extension.get_name() == 'IClear':
				iclear = extension
				
		from extensions.iclear.wiclear import IclearSettingDialog
		if iclear is not None:
			dialog = IclearSettingDialog(True, parent = self)
		else:
			from extensions.iclear.iclear_extension import IClearExtension
			dialog = IclearSettingDialog(False, parent = self)
		
		if dialog.exec_() == QDialog.Accepted:
			state, hostpath, sitepath = dialog.get_values()
		if state:
			self.settings.setValue("extensions/iclear", '1')
		else:
			self.settings.setValue("extensions/iclear", '0')
		self.settings.sync()
		'''
	def toggle_extension(self, extension):
		for dock in self.findChildren(QDockWidget):
			if dock.windowTitle() == extension.get_name():
				dock.setVisible(not dock.isVisible())
				break

	def ic_create_iclear_tool(self):
		
		iclear_support = self.settings.value("iclear/support", 0)
		self.iclear_support = True if iclear_support == '1' else False
		
		if not self.iclear_support:
			return
			
		if 'iclear' not in sys.modules:
			import libiclear.iclear as iclear
			import libiclear.wiclear as wiclear
			iclear.Tools.set_output(stdout= False, outhandler = self.on_message)
			
		self.iclear_hostpath = self.settings.value("iclear/hostpath", '') or ''
		self.iclear_sitepath = self.settings.value("iclear/sitepath", '') or ''
		
		host = iclear.IHost("iclear", self.iclear_hostpath, self.iclear_sitepath)
		host.fill(fill_sites = True, fill_mans = True)
		nodnav = iclear.NodesNav(host = host)
		self.iclear_widget = wiclear.IclearWidget(nodnav, parent=self)
		self.iclear_tool_bar = self.addToolBar('iclear')
		self.iclear_tool_bar.addWidget(self.iclear_widget)
		
		self.tab_panel.currentChanged.connect(
			lambda: self.iclear_widget.fill_from_page_path(self.tab_panel.get_current_path()))
			
	def ic_turn_iclear_support(self):
		
		if 'iclear' not in sys.modules:
			import libiclear.iclear as iclear
			import libiclear.wiclear as wiclear
			iclear.Tools.set_output(stdout= False, outhandler = self.on_message)
		if self.iclear_support:
			iclear_hostpath = self.iclear_hostpath
			iclear_sitepath = self.iclear_sitepath
		else:
			iclear_hostpath = self.settings.value("iclear/hostpath", '') or ''
			iclear_sitepath = self.settings.value("iclear/sitepath", '') or ''

		dialog = wiclear.IclearSettingDialog(self.iclear_support,
			hostpath = iclear_hostpath, sitepath = iclear_sitepath, parent = self)
		if dialog.exec_() == QDialog.Accepted:
			state, hostpath, sitepath = dialog.get_values()
			if state:
				if hostpath.strip() != '':
					path = Path(hostpath.strip())
					full_path = Path(os.path.join(hostpath.strip(), sitepath.strip()))
					if path.exists() and full_path.exists():
						self.iclear_support = True
						self.iclear_hostpath = hostpath.strip()
						self.iclear_sitepath = sitepath.strip()
						self.settings.setValue("iclear/hostpath", self.iclear_hostpath)
						self.settings.setValue("iclear/sitepath", self.iclear_sitepath)
						if not hasattr(self, 'iclear_tool_bar'):
							self.ic_create_iclear_tool()
						else:
							self.iclear_tool_bar.setVisible(True)
					else:
						self.new_message.emit(f"No such file {hostpath}", 'warning') 
				else:
					self.new_message.emit(f"Hostpath not specified", 'info')  
			else:
				self.iclear_support = False
				if hasattr(self, 'iclear_tool_bar'):
					self.iclear_tool_bar.setVisible(False)
					
		if self.iclear_support:
			self.settings.setValue("iclear/support", '1')
			self.settings.setValue("iclear/hostpath", self.iclear_hostpath)
			self.settings.setValue("iclear/sitepath", self.iclear_sitepath)
		else:
			self.settings.setValue("iclear/support", '0')
		
		self.settings.sync()
		
		'''
		
		
	def on_error(self, msg):
		self.new_error.emit(msg)
		
	def on_message(self, msg, msgtype=None):
		if msgtype:
			self.new_message.emit(msg, msgtype)
		else:
			self.new_message.emit(msg, '')
		
	def set_tab_panel(self):
		open_files = []
		open_files_size = self.settings.beginReadArray("open_files")
		for i in range(open_files_size):
			self.settings.setArrayIndex(i)
			open_files.append(self.settings.value("f"))
		self.settings.endArray()
		
		if len(open_files)>0:
			for file_path in open_files:
				self.tab_panel.add_tab(Path(file_path)) 
		if (self.tab_panel.count()==0):
			self.tab_panel.new_tab()
					
	def optional_action(self):
		action = self.sender()
		method_name = action.data()
		getattr(self.tab_panel.get_current_editor().editor, method_name)()
		
	def create_action(self, menu, name, connection,
			icon=None, shortcut=None, statustip=None, tooltip=None, data=None):
		action = menu.addAction(name)
		action.triggered.connect(connection)
		if icon: action.setIcon(QIcon(icon))
		if shortcut: action.setShortcut(shortcut)
		if statustip: action.setStatusTip(statustip)
		if tooltip: action.setToolTip(tooltip)
		if data: action.setData(data)
		return action
		
	def create_menu_from_list(self, menu, action_list):
		for action in action_list:
			data=action['action']
			if data == 'menu':
				submenu = menu.addMenu(action['name'])
				if action.get('content') is not None:
					self.create_menu_from_list(submenu, action['content'])
			elif data == 'separator':
				menu.addSeparator()
			else:
				self.create_action(menu, action['name'], self.optional_action, data=action['action'],
					icon=action.get('icon'), shortcut=action.get('shortcut'), 
						statustip=action.get('statustip'), tooltip=action.get('tooltip'))
			
	def create_menu_bar(self):
		
		menu_bar = self.menuBar()
		
		# File Menu
		file_menu = menu_bar.addMenu("File")

		self.create_action(file_menu, "New", self.tab_panel.new_tab, shortcut="Ctrl+N")
		self.create_action(file_menu, "Open", self.tab_panel.open_file, shortcut="Ctrl+O", statustip="Open File")
		self.create_action(file_menu, "Save", self.tab_panel.current_tab_save, shortcut="Ctrl+S")
		self.create_action(file_menu, "Save As", self.tab_panel.current_tab_save_as, shortcut="Ctrl+Shift+S")
		self.create_action(file_menu, "Reload", self.tab_panel.current_tab_reload, shortcut="Ctrl+Shift+R")
		
		file_menu.addSeparator()
		self.create_action(file_menu, "Property", self.tab_panel.current_tab_view_property)
		file_menu.addSeparator()
 
		self.recent_files_menu = file_menu.addMenu("Recent files")
		self.create_recent_files_menu()

		file_menu.addSeparator()
		
		self.create_action(file_menu, "Exit", self.close, shortcut="Ctrl+Q")

		# optional Menu 
		if hasattr(self.editor_class, 'class_actions'):
			for i in self.editor_class.class_actions:
				if i['action'] == 'menu':
					menu = menu_bar.addMenu(i['name'])
					self.create_menu_from_list(menu, i['content'])
				
		# Tool menu
		tool_menu = menu_bar.addMenu('Tool')
		
		self.create_action(tool_menu, "Zoom In", self.zoom_in, shortcut=QKeySequence.ZoomIn)
		self.create_action(tool_menu, "Zoom Out", self.zoom_out, shortcut=QKeySequence.ZoomOut)
		tool_menu.addSeparator()
		self.extensions_menu = tool_menu.addMenu("Extensions")
				
	def create_toolbar(self):
		if hasattr(self.editor_class, 'class_actions'):
			for i in self.editor_class.class_actions:
				if i['action'] == 'tool':
					tool = self.addToolBar(i['name'])
					self.create_menu_from_list(tool, i['content'])
					

	def on_editor_state_changed(self, name, fname, mod_label, operation):
		dash = '' if name == '' else '- '
		self.setWindowTitle(f'{mod_label}{fname} {dash}TabPanel')
		if operation in ['Opened', 'Saved', 'Saved as', 'Reload']:
			self.set_status_bar_msg(f'{operation} {name}')
			self.new_message.emit(f'{operation} {name}', 'info')
		if operation in ['Opened', 'Saved as', 'Reopened']:
			self.add_recent_file(fname)
			
	def create_status_bar(self):
		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		self.status_msg_box = QLabel(parent=self)
		self.statusBar.addPermanentWidget(self.status_msg_box)
		self.statusBar.showMessage("Ready")
		
	def set_permanent_status_msg(self, msg):
		self.status_msg_box.setText(f"Line: {msg}")

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
		self.recent_files = []
		recent_files_size = self.settings.beginReadArray("recent_files")
		for i in range(recent_files_size):
			self.settings.setArrayIndex(i)
			self.recent_files.append(self.settings.value("f"))
		self.settings.endArray()

	def saveSettings(self, open_files):
		font_point_size = self.font().pointSize()
		self.settings.setValue("geometry/size", self.size()) 
		self.settings.setValue("geometry/pos", self.pos())
		self.settings.setValue("font_point_size", font_point_size)

		self.settings.beginWriteArray("recent_files")
		for i, el in enumerate(self.recent_files):
			self.settings.setArrayIndex(i)
			self.settings.setValue("f", el)
		self.settings.endArray()

		self.settings.beginWriteArray("open_files")
		for i, el in enumerate(open_files):
			self.settings.setArrayIndex(i)
			self.settings.setValue("f", el)
		self.settings.endArray()
		
		self.settings.sync()
		
			
class ErrorHandler():

	def __init__(self, handle):
		self.original_stderr = sys.stderr
		self.handle = handle

	def write(self, message):
		self.original_stderr.write(message)
		#self.original_stderr.flush()
		self.handle(message)
		
	def flush(self):
		self.original_stderr.flush()
		
if __name__ == "__main__":

	app = QApplication(sys.argv)
	clear_editor = ClearEditor(editor_class=HTMLEditor)	
	clear_editor.setWindowIcon(QIcon('icons/clear.svg'))
	
	original_stderr = sys.stderr
	sys.stderr = ErrorHandler(clear_editor.on_error)
	
	clear_editor.show()
	
	app_exit_code = app.exec_()
	sys.stderr = original_stderr
	sys.exit(app_exit_code) 	

 
