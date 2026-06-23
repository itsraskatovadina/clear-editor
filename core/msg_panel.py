#! /usr/bin/env python3

from PyQt5.QtWidgets import QTabWidget, QTextEdit, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
import sys


class MsgPanel(QTabWidget):
    new_error = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MsgPanel, self).__init__(parent)

        self.err_box = QTextEdit(self)
        self.err_box.setReadOnly(True)
        self.msg_box = QTextEdit(self)
        self.msg_box.setReadOnly(True)
        self.view_box = QTextEdit(self)

        self.addTab(self.err_box, "Err")
        self.addTab(self.msg_box, "Msg")
        self.addTab(self.view_box, "View")
        self.setTabPosition(QTabWidget.West)
        self.setUsesScrollButtons(True)
        self.setCurrentIndex(0)
        self.app = QApplication.instance() if (QApplication.instance() is not None) else QApplication(sys.argv)

        self.new_error.connect(self._display_error)

    def _display_error(self, msg):
        self.err_box.append(f"<span style='color: red;'>{msg}</span>")
        self.setCurrentWidget(self.err_box)
        self.app.beep()

    def new_message(self, msg, sender=None, msgtype=None):
        colors = {'debug': 'gray', 'info': 'blue', 'warning': 'orange', 'error': 'red'}
        color = colors.get(msgtype, 'blue')
        prefix = f"[{sender}] " if sender else ""
        self.msg_box.append(f"<span style='color: {color};'>{prefix}{msg}</span>")
        self.setCurrentWidget(self.msg_box)
        self.app.beep()

    def new_view(self, text, text_type='plain'):
        self.view_box.clear()
        if text_type == 'html':
            self.view_box.setHtml(text)
        else:
            self.view_box.setPlainText(text)
        self.setCurrentWidget(self.view_box)


class ErrorHandler:
    def __init__(self, handle):
        self.original_stderr = sys.stderr
        self.handle = handle

    def write(self, message):
        self.original_stderr.write(message)
        self.handle(message)

    def flush(self):
        self.original_stderr.flush()
