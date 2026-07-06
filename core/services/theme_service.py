from PyQt5.QtCore import QObject
from PyQt5.QtGui import QFont, QColor


class ThemeService(QObject):
    def __init__(self, target=None, parent=None):
        super().__init__(parent)
        self._target = target
        self._default_font = target.font() if target else None

    def zoom_in(self):
        font = self._target.font()
        font.setPointSize(font.pointSize() + 1)
        self._target.setFont(font)

    def zoom_out(self):
        font = self._target.font()
        font.setPointSize(max(6, font.pointSize() - 1))
        self._target.setFont(font)

    def set_font(self, font: QFont):
        self._target.setFont(font)

    def set_font_size(self, pts: int):
        font = self._target.font()
        font.setPointSize(pts)
        self._target.setFont(font)

    def set_background(self, color: QColor):
        self._target.setStyleSheet(
            f"QMainWindow {{ background-color: {color.name()}; }}"
        )

    def reset(self):
        self._target.setFont(self._default_font)
        self._target.setStyleSheet("")
