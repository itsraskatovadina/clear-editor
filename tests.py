#! /usr/bin/python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from pathlib import Path
import sys
import os

class Editor_Win(QMainWindow):
	''' for debugging '''
	def __init__(self, parent=None, editor_class=QTextEdit):
		super(QMainWindow, self).__init__()
		
		self.editor_class = editor_class 
		self.file_editor = FileEditor(self, editor_class=editor_class)
		
		self.setWindowTitle(f'FileEditor')
		central_widget = QWidget(self)
		self.setCentralWidget(central_widget)
		layout = QVBoxLayout(central_widget)
		self.file_name = QLabel(self)
		layout.addWidget(self.file_name)
		layout.addWidget(self.file_editor)
		
		#self.file_editor.editor.document().modificationChanged.connect(self.on_editor_modification_changed)
		self.file_editor.cursor_position_changed.connect(self.on_cursor_position_changed)
		self.file_editor.user_modification_changed.connect(self.on_user_modification_changed)
		
		self.create_menu_bar()
		self.create_toolbar()
		self.create_status_bar()
		
		#self.on_editor_modification_changed()
		self.on_cursor_position_changed(self.file_editor.editor.textCursor().blockNumber() + 1) 
		
		self.file_editor.emit_user_modification_changed()
	'''
	def on_editor_modification_changed(self):
		self.text_modified.setText(f'Modified: {str(self.file_editor.editor.document().isModified())}')
	'''
	def set_file_names(self, name, fname, mod_label):
		self.setWindowTitle(f'{mod_label}{fname} - FileEditor')
		self.file_name.setText(f'File name: {name}')
		
	def on_user_modification_changed(self, name, fname, mod_label):
		self.set_file_names(name, fname, mod_label)
		#if operation in ['Opened', 'Saved']: self.on_status_bar_message(f'{operation} {name}')
		
	def on_cursor_position_changed(self, line_num):
		self.cursor_line.setText(f'Line: {str(line_num)}')
		
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
					
	def optional_action(self):
		action = self.sender()
		method_name = action.data()
		getattr(self.file_editor.editor, method_name)()
		
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
				self.create_menu_from_list(submenu, action['content'])
			elif data == 'separator':
				menu.addSeparator()
			else:
				self.create_action(menu, action['name'], self.optional_action, data=action['action'],
					icon=action.get('icon'), shortcut=action.get('shortcut'), 
						statustip=action.get('statustip'), tooltip=action.get('tooltip'))
						
	def create_menu_bar(self):
		menu_bar = self.menuBar()
		file_menu = menu_bar.addMenu("File")
		file_menu.addAction('Open', self.open_file)
		file_menu.addAction('Save', self.save_file)
		file_menu.addAction('Save As ', self.save_as_file)
		
		if hasattr(self.editor_class, 'class_actions'):
			for i in self.editor_class.class_actions:
				if i['action'] == 'menu':
					menu = menu_bar.addMenu(i['name'])
					self.create_menu_from_list(menu, i['content'])
					
	def create_toolbar(self):
		if hasattr(self.editor_class, 'class_actions'):
			for i in self.editor_class.class_actions:
				if i['action'] == 'tool':
					tool = self.addToolBar(i['name'])
					self.create_menu_from_list(tool, i['content'])
		
	def create_status_bar(self):
		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		#self.text_modified = QLabel(self)
		#self.statusBar.addPermanentWidget(self.text_modified)
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
		if self.file_editor.isModified(): print('Error self.file_editor.isModified() = True')
		
	def save_file(self):
		if self.file_editor.path is None:
			return self.save_as_file()
		self.file_editor.save_to_file()
		self.set_file_names(self.file_editor.path.name, str(self.file_editor.path), '')
		if self.file_editor.isModified(): print('Error self.file_editor.isModified() = True')
		
	def save_as_file(self):
		file_path = QFileDialog.getSaveFileName(self, "Save As")[0]
		if file_path == '':
			return 	
		self.file_editor.save_as_file(Path(file_path))
		self.set_file_names(self.file_editor.path.name, file_path, '')

class Tab_Win(QMainWindow):
	''' for debugging '''
	def __init__(self):
		super(QMainWindow, self).__init__()
		
		self.setWindowTitle(f'TabPanel')
		self.tab_panel = TabPanel()
		self.setCentralWidget(self.tab_panel)
		
		self.tab_panel.editor_state_changed.connect(self.on_editor_state_changed)
		self.tab_panel.editor_cursor_position_changed.connect(self.on_cursor_position_changed)
		
		self.tab_panel.new_tab()
		
		self.create_status_bar()
		menu_bar = self.menuBar()
		file_menu = menu_bar.addMenu("File")
		file_menu.addAction('New', self.tab_panel.new_tab)
		file_menu.addAction('Open', self.tab_panel.open_file)
		file_menu.addAction('Save', self.tab_panel.current_tab_save)
		file_menu.addAction('Save As ', self.tab_panel.current_tab_save_as)
		file_menu.addSeparator()
		file_menu.addAction('Reload', self.tab_panel.current_tab_reload)
		file_menu.addSeparator()
		file_menu.addAction('Property', self.tab_panel.current_tab_view_property)

	def on_editor_state_changed(self, name, fname, mod_label, operation):
		dash = '' if name == '' else '- '
		self.setWindowTitle(f'{mod_label}{fname} {dash}TabPanel')
		if operation in ['Opened', 'Saved', 'Saved as', 'Reload']:
			self.on_status_bar_message(f'{operation} {name}')
		
	def create_status_bar(self):
		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		self.cursor_line = QLabel(parent=self)
		self.statusBar.addPermanentWidget(self.cursor_line)
		self.statusBar.showMessage("Ready")
		
	def on_cursor_position_changed(self, line_num):
		self.cursor_line.setText(f'Line: {str(line_num)}')
		
	def on_status_bar_message(self, msg):
		self.statusBar.showMessage(f'{msg}', 2000)
		
	def open_file(self):
		# open file
		file_path, _ = QFileDialog.getOpenFileName(
			win, "Open File", "", "Text Files (*.txt);;All Files (*)")
		if file_path == '':
			return
		win.doc_tab_panel.add_tab(Path(file_path))
	
	def closeEvent(self, event):
		"""Handle application close event"""
		if self.tab_panel.close_all_tab():
			event.accept()
		else:
			event.ignore()
			
	def on_app_focus_changed(self, old, now):
		self.tab_panel.on_app_focus_changed(old, now)
		
if __name__ == "__main__":

	app = QApplication(sys.argv)
	
	from lib.text_editor import HTMLEditor
	
	# from lib.file_editor import FileEditor
	# win = Editor_Win(editor_class=HTMLEditor)
	
	from lib.file_tab_panel import TabPanel
	win = Tab_Win()
	
	app.focusChanged.connect(win.on_app_focus_changed)
	
	win.setWindowIcon(QIcon('icons/clear1.jpg'))
	win.show()
	sys.exit(app.exec())

