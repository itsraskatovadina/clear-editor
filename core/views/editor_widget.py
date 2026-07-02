#! /usr/bin/env python3

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QTextEdit, QHBoxLayout


class EditorWidget(QWidget):
    modification_changed = pyqtSignal()
    cursor_position_changed = pyqtSignal(int)

    def __init__(self, parent=None, editor_class=QTextEdit):
        super().__init__(parent)
        self.editor = editor_class(parent=self)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.editor)
        self.setLayout(hbox)

        self._programmatic_change = False
        self.editor.document().modificationChanged.connect(
            self._on_modification_changed
        )
        self.editor.cursorPositionChanged.connect(self._on_cursor_changed)

    def _on_modification_changed(self, flag):
        if not self._programmatic_change:
            self.modification_changed.emit()

    def _on_cursor_changed(self):
        line = self.editor.textCursor().blockNumber() + 1
        self.cursor_position_changed.emit(line)

    def set_text(self, text):
        self._programmatic_change = True
        self.editor.setPlainText(text)
        self._programmatic_change = False

    def get_text(self):
        return self.editor.toPlainText()

    def set_modified(self, flag):
        self.editor.document().setModified(flag)

    def is_modified(self):
        return self.editor.document().isModified()

    def text_cursor(self):
        return self.editor.textCursor()

    def set_text_cursor(self, cursor):
        self.editor.setTextCursor(cursor)

    def document(self):
        return self.editor.document()

    def set_focus(self):
        self.editor.setFocus()
