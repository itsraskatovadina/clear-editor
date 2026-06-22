#! /usr/bin/env python3

from plugins_service.plugin_base import PluginBase
from wiclear import IclearWidget


class IclearPlugin(PluginBase):
	name = "iclear"
	description = "Навигация и работа со структурой PHP-сайта itsclear.ru"

	def on_load(self, editor):
		self._editor = editor

	def on_unload(self):
		if self._editor and hasattr(self._editor, 'tab_panel'):
			try:
				self._editor.tab_panel.tab_added.disconnect(self._on_tab_added)
			except TypeError:
				pass
		self._editor = None
		self._widget = None

	def create_toolbar_widget(self, parent=None):
		self._widget = IclearWidget(parent=parent)
		if self._editor and hasattr(self._editor, 'tab_panel'):
			self._editor.tab_panel.tab_added.connect(self._on_tab_added)
		return self._widget

	def _on_tab_added(self, editor_widget):
		file_editor = editor_widget.parent()
		if hasattr(file_editor, 'path') and file_editor.path and self._widget:
			self._widget.fill_from_page_path(str(file_editor.path))
