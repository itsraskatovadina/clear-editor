#! /usr/bin/python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MsgBox(QTextEdit):
	def __init__(self, parent=None):
		super(MsgBox, self).__init__(parent)
		self.setReadOnly(True)
		
class ErrBox(QTextEdit):
	def __init__(self, parent=None):
		super(ErrBox, self).__init__(parent)
		self.setReadOnly(True)
		
class ViewBox(QTextEdit):
	def __init__(self, parent=None):
		super(ViewBox, self).__init__(parent)
		self.setReadOnly(True)
		
class MsgPanel(QTabWidget):
	
	def __init__(self, parent=None):
		super(MsgPanel, self).__init__(parent)
		
		self.err_box = QTextEdit(self)
		self.err_box.setReadOnly(True)
		self.msg_box = QTextEdit(self)
		self.view_box = QTextEdit(self)
		
		self.addTab(self.err_box, "Err")
		self.addTab(self.msg_box, "Msg")
		self.addTab(self.view_box, "View")
		self.setTabPosition(QTabWidget.West)
		self.setUsesScrollButtons(True)
		self.setCurrentIndex(0) 
		self.app = QApplication.instance() if (QApplication.instance() is not None) else QApplication(sys.argv)
		
	def new_message(self, msg, msgtype=None):
		self.msg_box.append(f"<span style='color: blue;'>{msg}</span>")
		#self.setCurrentIndex(1) 
		self.setCurrentWidget(self.msg_box)
		self.app.beep()
		
	def new_error(self, msg):
		#self.err_box.append(f"<span style='color: red;'>{msg.strip()}</span>")
		self.err_box.insertHtml(f"<span style='color: red;'>{msg}</span>")
		#self.setCurrentIndex(0) 
		self.setCurrentWidget(self.err_box)
		self.app.beep()
