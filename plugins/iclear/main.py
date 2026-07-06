#! /usr/bin/env python3

from plugins_service.plugin_base import PluginBase
from wiclear import IclearWidget


class IclearPlugin(PluginBase):
    name = "iclear"
    description = "Навигация и работа со структурой PHP-сайта itsclear.ru"

    def on_load(self, editor):
        self._editor = editor

    def on_unload(self):
        self._editor = None
        self._widget = None

    def create_toolbar_widget(self, parent=None):
        self._widget = IclearWidget(
            open_file_cb=self._editor.file_tab_srv.add_tab,
            parent=parent,
        )
        self._editor.file_tab_srv.editor_state_changed.connect(
            self._on_tab_changed
        )
        self._sync_from_current_tab()
        return self._widget

    def _on_tab_changed(self, title, full_title, mod_label, operation):
        if operation in ("tab_changed", "Opened", "Reload", "Reopened"):
            if full_title and self._widget:
                self._widget.fill_from_page_path(full_title)

    def _sync_from_current_tab(self):
        doc = self._editor.file_tab_srv.current_document()
        if doc and doc.file_path and self._widget:
            self._widget.fill_from_page_path(str(doc.file_path))
