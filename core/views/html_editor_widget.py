#! /usr/bin/env python3

from PyQt5.QtCore import QRegularExpression, Qt
from PyQt5.QtGui import QSyntaxHighlighter, QTextCursor, QTextCharFormat, QColor, QFont
from PyQt5.QtWidgets import QTextEdit

from core.models.html_editor_model import TagCompletionsModel


class HtmlHighlighter(QSyntaxHighlighter):
    tag_format = QTextCharFormat()
    tag_format.setForeground(QColor("blue"))
    tag_format.setFontWeight(QFont.Bold)

    quote_format = QTextCharFormat()
    quote_format.setForeground(QColor("green"))

    comment_format = QTextCharFormat()
    comment_format.setForeground(QColor("red"))

    tag_pattern = QRegularExpression(r"<[^>]+>")
    quote_pattern = QRegularExpression(r"'[^']*'")
    double_quote_pattern = QRegularExpression(r'"[^"]*"')
    comment_pattern = QRegularExpression(r"<!--(?:[^-]|-(?!-))*-->")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = [
            (self.tag_pattern, self.tag_format),
            (self.quote_pattern, self.quote_format),
            (self.double_quote_pattern, self.quote_format),
            (self.comment_pattern, self.comment_format),
        ]

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            match_iter = pattern.globalMatch(text)
            while match_iter.hasNext():
                match = match_iter.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class HTMLEditor(QTextEdit):
    def __init__(self, parent=None, completions: TagCompletionsModel = None):
        super().__init__(parent)

        self.highlighter = HtmlHighlighter(self.document())
        self._completions = completions or TagCompletionsModel()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Greater and self.hasFocus():
            cursor = self.textCursor()
            text = self.toPlainText()
            pos = cursor.position()
            before = text[:pos]
            last_lt = before.rfind("<")
            if last_lt == -1:
                super().keyPressEvent(event)
                return
            tag_candidate = before[last_lt + 1 : pos].strip()
            if not tag_candidate or tag_candidate.startswith("/"):
                super().keyPressEvent(event)
                return
            if self._completions.is_valid_tag(tag_candidate):
                cursor.insertText(">")
                closing_tag = f"</{tag_candidate}>"
                cursor.insertText(closing_tag)
                cursor.movePosition(
                    QTextCursor.Left, QTextCursor.MoveAnchor, len(closing_tag)
                )
                self.setTextCursor(cursor)
                return

        super().keyPressEvent(event)
