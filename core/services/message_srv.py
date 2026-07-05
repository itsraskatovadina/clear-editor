#! /usr/bin/env python3

import sys

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication

from core.models.message_model import Message


class MessageSrv(QObject):
    display_error = pyqtSignal(str)
    display_message = pyqtSignal(str)
    message_received = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def post_message(self, text, sender="", msg_type="info"):
        msg = Message(text=text, sender=sender, msg_type=msg_type)
        html = self._format(msg)
        if msg_type == "error":
            self.display_error.emit(html)
            QApplication.beep()
        elif msg_type == "warning":
            self.display_message.emit(html)
            QApplication.beep()
        else:
            self.display_message.emit(html)
        self.message_received.emit()

    def _format(self, msg):
        colors = {"debug": "gray", "info": "blue", "warning": "#cc8400", "error": "red"}
        color = colors.get(msg.msg_type, "blue")
        prefix = f"[{msg.sender}] " if msg.sender else ""
        return f"<span style='color: {color};'>{prefix}{msg.text}</span>"


class ErrorHandler:
    def __init__(self, handle):
        self.original_stderr = sys.stderr
        self.handle = handle

    def write(self, message):
        self.original_stderr.write(message)
        self.handle(message)

    def flush(self):
        self.original_stderr.flush()
