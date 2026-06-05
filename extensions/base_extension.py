#! /usr/bin/python3

# extensions/base_extension.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, QObject

class BaseExtension(QObject):
    """Базовый класс для всех расширений"""
    
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
    
    def get_name(self):
        raise NotImplementedError
    
    def on_close(self):
        pass
