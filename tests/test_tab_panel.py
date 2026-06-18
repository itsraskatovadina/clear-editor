#! /usr/bin/env python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon

from pathlib import Path
import sys

from core.tab_panel import TabPanel


class Tab_Win(QMainWindow):
	def __init__(self):
		super(QMainWindow, self).__init__()

		self.setWindowTitle('TabPanel')
		self.tab_panel = TabPanel()
		self.setCentralWidget(self.tab_panel)
		#self.tab_panel.new_tab()

		self.tab_panel.editor_state_changed.connect(self.on_editor_state_changed)
		self.tab_panel.line_changed.connect(self.on_line_changed)
		self.tab_panel.message.connect(self.on_message)

		self.create_status_bar()
		menu_bar = self.menuBar()
		file_menu = menu_bar.addMenu("File")
		file_menu.addAction('New', self.tab_panel.new_tab)
		file_menu.addAction('Open', self.tab_panel.open_file)
		file_menu.addAction('Save', self.tab_panel.current_tab_save)
		file_menu.addAction('Save As', self.tab_panel.current_tab_save_as)
		file_menu.addSeparator()
		file_menu.addAction('Reload', self.tab_panel.current_tab_reload)
		file_menu.addSeparator()
		file_menu.addAction('Property', self.tab_panel.current_tab_view_property)

	def on_editor_state_changed(self, name, fname, mod_label, operation):
		dash = '' if name == '' else '- '
		self.setWindowTitle(f'{mod_label}{fname} {dash}TabPanel')
		if operation in ['Opened', 'Saved', 'Saved as', 'Reload']:
			self.on_status_bar_message(f'{operation} {name}')
			
	def on_message(self, msg, sender=None, msgtype=None):
		print(msg, sender, msgtype)

	def create_status_bar(self):
		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		self.cursor_line = QLabel(parent=self)
		self.statusBar.addPermanentWidget(self.cursor_line)
		self.statusBar.showMessage("Ready")

	def on_line_changed(self, line_num):
		self.cursor_line.setText(f'Line: {str(line_num)}')

	def on_status_bar_message(self, msg):
		self.statusBar.showMessage(f'{msg}', 2000)

	def closeEvent(self, event):
		if self.tab_panel.close_all_tab():
			event.accept()
		else:
			event.ignore()

if __name__ == "__main__":
	app = QApplication(sys.argv)

	win = Tab_Win()

	app.focusChanged.connect(win.tab_panel.on_app_focus_changed)

	win.setWindowIcon(QIcon('icons/clear_test.jpg'))
	win.show()
	sys.exit(app.exec())
