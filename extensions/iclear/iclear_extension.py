#! /usr/bin/python3

from PyQt5.QtCore import Qt, pyqtSignal
from ..base_extension import BaseExtension
from .wiclear import IclearWidget, IclearSettingDialog

class IClearExtension(BaseExtension):

	def __init__(self, parent=None):
		super().__init__(parent)
		self.widget = None
		
	def get_name(self):
		return 'IClear'
		
	def create_widget(self):
		
		self.widget = IclearWidget()
		#self.widget.setWindowTitle(self.get_name())
		return self.widget
