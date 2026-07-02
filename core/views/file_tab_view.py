#! /usr/bin/env python3

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTabWidget


class FileTabView(QTabWidget):
    close_requested = pyqtSignal(int)
    current_changed = pyqtSignal(int)
    tab_moved = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self._on_close_requested)
        self.currentChanged.connect(self._on_current_changed)
        self.tabBar().tabMoved.connect(self._on_tab_moved)

    def _on_close_requested(self, index):
        self.close_requested.emit(index)

    def _on_current_changed(self, index):
        self.current_changed.emit(index)

    def _on_tab_moved(self, from_idx, to_idx):
        self.tab_moved.emit(from_idx, to_idx)

    def add_editor_tab(self, widget, title, tooltip=""):
        index = self.addTab(widget, title)
        if tooltip:
            self.setTabToolTip(index, tooltip)
        return index

    def set_tab(self, index, text, tooltip=""):
        self.setTabText(index, text)
        if tooltip:
            self.setTabToolTip(index, tooltip)

    def remove_editor_tab(self, index):
        self.removeTab(index)

    def editor_at(self, index):
        return self.widget(index)
