#! /usr/bin/env python3

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QListView,
    QVBoxLayout,
)


class PluginWidget(QDialog):
	def __init__(self, available, active_names, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Plugin Manager")
		self.resize(300, 400)

		self._available = available
		self._active_names = active_names.copy()

		layout = QVBoxLayout(self)
		self.list_plugins = QListView(self)
		layout.addWidget(self.list_plugins)

		self._model = QStandardItemModel(self)
		self.list_plugins.setModel(self._model)

		buttons = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
		)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)
		layout.addWidget(buttons)

		self._populate()

	def _populate(self):
		for plugin in self._available:
			item = QStandardItem(plugin["name"])
			item.setData(plugin["name"], Qt.UserRole)
			item.setToolTip(plugin.get("description", ""))
			item.setCheckable(True)
			item.setCheckState(
				Qt.Checked if plugin["name"] in self._active_names
				else Qt.Unchecked
			)
			self._model.appendRow(item)

	def get_selected_names(self):
		names = set()
		for i in range(self._model.rowCount()):
			item = self._model.item(i)
			if item.checkState() == Qt.Checked:
				names.add(item.data(Qt.UserRole))
		return names
