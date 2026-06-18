#! /usr/bin/env python3

from PyQt5.QtCore import pyqtSignal

from plugins_service.plugin_base import PluginBase


class WordCountPlugin(PluginBase):
	name = "wordcount"
	description = "Подсчёт слов в редакторе"
	word_count_changed = pyqtSignal(int)

	status_fields = {
		"word_count": {
			"label_template": "Word: {}",
			"signal_name": "word_count_changed",
		}
	}

	def on_load(self, editor):
		self._panel = editor.tab_panel
		self._connected = []
		for i in range(self._panel.count()):
			self._panel.widget(i).editor.textChanged.connect(self._count_words)
			self._connected.append(self._panel.widget(i).editor)
		self._panel.currentChanged.connect(self._on_tab_changed)
		self._panel.tab_added.connect(self._on_tab_added)
		self._count_words()

	def on_unload(self):
		for ed in self._connected:
			try:
				ed.textChanged.disconnect(self._count_words)
			except TypeError:
				pass
		self._panel.currentChanged.disconnect(self._on_tab_changed)
		self._panel.tab_added.disconnect(self._on_tab_added)
		self._panel = None
		self._connected = []

	def _on_tab_added(self, editor_widget):
		editor_widget.textChanged.connect(self._count_words)
		self._connected.append(editor_widget)

	def _on_tab_changed(self, index):
		self._count_words()

	def _count_words(self):
		current = self._panel.currentWidget()
		if current is None:
			return
		text = current.editor.toPlainText()
		count = len(text.split()) if text.strip() else 0
		self.word_count_changed.emit(count)
