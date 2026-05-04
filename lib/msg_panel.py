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
		
		self.msg_box = MsgBox(self)
		self.err_box = ErrBox(self)
		self.view_box = ViewBox(self)
		
		self.addTab(self.err_box, "Err")
		self.addTab(self.msg_box, "Msg")
		self.addTab(self.view_box, "View")
		self.setTabPosition(QTabWidget.West)
		self.setUsesScrollButtons(True)
		self.setCurrentIndex(0) 
 
