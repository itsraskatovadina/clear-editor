#! /usr/bin/env python3

from PyQt5.QtCore import pyqtSignal

from plugins_service.plugin_base import PluginBase


class WordCountPlugin(PluginBase):
    name = "wordcount"
    description = "Word counter in status bar"

    status_fields = {
        "word_count": {
            "label_template": "Word: {}",
            "signal_name": "word_count_changed",
        }
    }

    word_count_changed = pyqtSignal(int)

    def on_load(self, editor):
        self._editor = editor
        self._connected = set()

        for i in range(editor.file_tab_srv.tab_count()):
            self._connect_editor_at(i)

        editor.file_tab_srv.editor_state_changed.connect(self._on_editor_state)
        editor.file_tab_view.current_changed.connect(self._on_tab_switch)

        self._update_count()

    def on_unload(self):
        if self._editor:
            self._editor.file_tab_srv.editor_state_changed.disconnect(
                self._on_editor_state
            )
            self._editor.file_tab_view.current_changed.disconnect(
                self._on_tab_switch
            )
            srv = self._editor.file_tab_srv
            for ew_id in list(self._connected):
                idx = self._find_index_by_id(ew_id)
                if idx >= 0:
                    srv.with_editor(idx, lambda e: e.textChanged.disconnect(self._update_count))
        self._connected.clear()
        self._editor = None

    def _connect_editor_at(self, index):
        srv = self._editor.file_tab_srv
        ew = srv.widget_at(index)
        if ew is None or id(ew) in self._connected:
            return
        self._connected.add(id(ew))
        srv.with_editor(index, lambda e: e.textChanged.connect(self._update_count))

    def _find_index_by_id(self, wid):
        if not self._editor:
            return -1
        srv = self._editor.file_tab_srv
        for i in range(srv.tab_count()):
            if id(srv.widget_at(i)) == wid:
                return i
        return -1

    def _on_editor_state(self, name, fname, mod_label, operation):
        if operation in ("Opened", "New"):
            srv = self._editor.file_tab_srv
            count = srv.tab_count()
            if count:
                self._connect_editor_at(count - 1)

    def _on_tab_switch(self, index):
        self._update_count()

    def _update_count(self):
        editor_widget = self._editor.current_editor()
        if editor_widget is None:
            self.word_count_changed.emit(0)
            return
        text = editor_widget.toPlainText()
        count = len(text.split()) if text.strip() else 0
        self.word_count_changed.emit(count)
