from PyQt5.QtCore import QObject
from PyQt5.QtGui import QFont


class ZoomService(QObject):
    def __init__(self, target, parent=None):
        super().__init__(parent)
        self._target = target

    def zoom_in(self):
        font = self._target.font()
        font.setPointSize(font.pointSize() + 1)
        self._target.setFont(font)

    def zoom_out(self):
        font = self._target.font()
        font.setPointSize(max(6, font.pointSize() - 1))
        self._target.setFont(font)
