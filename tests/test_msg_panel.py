#! /usr/bin/env python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon

import sys
import traceback

from core.msg_panel import MsgPanel, ErrorHandler

class MyCustomError(Exception):
    pass
    
class Msg_Win(QMainWindow):
	def __init__(self):
		super(QMainWindow, self).__init__()

		self.setWindowTitle('MsgPanel')
		self.msg_panel = MsgPanel()
		self.setCentralWidget(self.msg_panel)

		menu_bar = self.menuBar()
		test_menu = menu_bar.addMenu("Test")
		test_menu.addAction('Debug', lambda: self.msg_panel.new_message("debug message", "test", "debug"))
		test_menu.addAction('Info', lambda: self.msg_panel.new_message("info message", "test", "info"))
		test_menu.addAction('Warning', lambda: self.msg_panel.new_message("warning message", "test", "warning"))
		test_menu.addAction('Error', lambda: self.msg_panel.new_message("error message", "test", "error"))
		test_menu.addSeparator()
		test_menu.addAction('Simulated Error (stderr)', lambda: self.simulated_error())

	def on_error(self, msg):
		self.msg_panel.new_error.emit(msg)

	def simulated_error(self):
		raise MyCustomError("Simulated MyCustomError")
		
if __name__ == "__main__":
	app = QApplication(sys.argv)

	win = Msg_Win()

	original_stderr = sys.stderr
	sys.stderr = ErrorHandler(win.on_error)

	def excepthook(exc_type, exc_value, exc_tb):
		msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
		original_stderr.write(msg)
		win.on_error(msg)

	sys.excepthook = excepthook

	win.setWindowIcon(QIcon('icons/clear_test.jpg'))
	win.show()
	
	app_exit_code = app.exec_()
	sys.stderr = original_stderr
	sys.exit(app_exit_code) 
