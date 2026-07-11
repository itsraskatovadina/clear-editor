#! /usr/bin/env python3

from PyQt5.QtWidgets import QTabWidget, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette


class MsgPanelView(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.err_box = QTextEdit(self)
        self.err_box.setReadOnly(True)
        palette = self.err_box.palette()
        palette.setColor(QPalette.Base, QColor("black"))
        palette.setColor(QPalette.Text, QColor("white"))
        self.err_box.setPalette(palette)
        self.msg_box = QTextEdit(self)
        self.msg_box.setReadOnly(True)
        self.view_box = QTextEdit(self)
        self.view_box.setReadOnly(True)

        self.addTab(self.msg_box, "Msg")
        self.addTab(self.view_box, "View")
        self.addTab(self.err_box, "Err")
        self.setTabPosition(QTabWidget.West)
        self.setUsesScrollButtons(True)
        self.setCurrentIndex(0)

    def append_err(self, html):
        self.err_box.append(html)
        self.setCurrentWidget(self.err_box)

    def append_msg(self, html):
        self.msg_box.append(html)
        self.setCurrentWidget(self.msg_box)

    def show_view(self, text, text_type="plain"):
        self.view_box.clear()
        if text_type == "html":
            self.view_box.setHtml(text)
        else:
            self.view_box.setPlainText(text)
        self.setCurrentWidget(self.view_box)
