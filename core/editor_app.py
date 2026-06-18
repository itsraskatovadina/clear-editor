#! /usr/bin/env python3

import json
from pathlib import Path

from PyQt5.QtWidgets import QMainWindow, QStatusBar, QSplitter, QLabel
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QPoint, QSize, QSettings, pyqtSignal

from core.tab_panel import TabPanel
from core.ext_editor import ExtEditor
from core.msg_panel import MsgPanel


class ConfigError(Exception):
	pass


class EditorApp(QMainWindow):
	win_title = "Text Editor"
	recent_files_changed = pyqtSignal()

	def __init__(self):
		super().__init__()
		self.setWindowTitle(EditorApp.win_title)
		self.setWindowIcon(QIcon('icons/clear.svg'))
		self.config = None
		self.settings = None
		self.recent_files = []

		self.tab_panel = TabPanel(parent=self, editor_class=ExtEditor)
		self.msg_panel = MsgPanel(parent=self)
		self.tab_panel.message.connect(self.on_message)
		self.tab_panel.editor_state_changed.connect(self.on_editor_state_changed)
		
		self.splitter = QSplitter(Qt.Vertical)
		self.splitter.addWidget(self.tab_panel)
		self.splitter.addWidget(self.msg_panel)
		self.splitter.setSizes([500, 100])
		self.setCentralWidget(self.splitter)

		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)

		self.line_label = QLabel(parent=self.statusBar)
		self.statusBar.addPermanentWidget(self.line_label)
		self.tab_panel.line_changed.connect(
			lambda line: self.line_label.setText(f"Line: {line}")
		)

	def load_config(self):
		config_path = Path("config.json")
		if not config_path.exists():
			raise ConfigError("Отсутствует файл конфигурации config.json")
		try:
			with open(config_path, encoding="utf-8") as f:
				self.config = json.load(f)
		except json.JSONDecodeError as e:
			raise ConfigError(f"Ошибка парсинга config.json: {e}")

		self.settings = QSettings("settings.ini", QSettings.IniFormat)

		ui_defaults = self.config.get("ui_defaults", {})
		pos = self.settings.value("geometry/pos")
		if not pos:
			default_pos = ui_defaults.get("geometry/pos", [200, 150])
			pos = QPoint(*default_pos)
		self.move(pos)

		size = self.settings.value("geometry/size")
		if not size:
			default_size = ui_defaults.get("geometry/size", [1500, 900])
			size = QSize(*default_size)
		self.resize(size)

		font_size = int(self.settings.value("font_size", 12))
		self.setFont(QFont("SansSerif", font_size))

		count = self.settings.beginReadArray("recent_files")
		for i in range(count):
			self.settings.setArrayIndex(i)
			f = self.settings.value("f")
			if f:
				self.recent_files.append(f)
		self.settings.endArray()

	def closeEvent(self, event):
		if self.settings is not None:
			self.settings.setValue("geometry/pos", self.pos())
			self.settings.setValue("geometry/size", self.size())
			font = self.font()
			self.settings.setValue("font_size", font.pointSize())

			self.settings.beginWriteArray("recent_files")
			for i, f in enumerate(self.recent_files):
				self.settings.setArrayIndex(i)
				self.settings.setValue("f", f)
			self.settings.endArray()

			open_files = self.tab_panel.get_open_files()
			self.settings.beginWriteArray("open_files")
			for i, f in enumerate(open_files):
				self.settings.setArrayIndex(i)
				self.settings.setValue("f", f)
			self.settings.endArray()

			self.settings.sync()
		event.accept()

	def zoom_in(self):
		font = self.font()
		font.setPointSize(font.pointSize() + 1)
		self.setFont(font)

	def zoom_out(self):
		font = self.font()
		font.setPointSize(max(6, font.pointSize() - 1))
		self.setFont(font)

	def add_recent_file(self, path):
		if path in self.recent_files:
			self.recent_files.remove(path)
		self.recent_files.insert(0, path)
		if len(self.recent_files) > 10:
			self.recent_files = self.recent_files[:10]

	def action_open_recent_file(self):
		action = self.sender()
		full_path = action.data()
		path = Path(full_path)
		self.tab_panel.add_tab(path)

	def action_clear_recent_files(self):
		self.recent_files = []
		self.recent_files_changed.emit()

	def current_editor(self):
		return self.tab_panel.current_editor()

	def set_tab_panel(self):
		file_list = []
		if self.settings is not None:
			count = self.settings.beginReadArray("open_files")
			for i in range(count):
				self.settings.setArrayIndex(i)
				f = self.settings.value("f")
				if f:
					file_list.append(f)
			self.settings.endArray()

		if len(file_list) != 0:
			self.tab_panel.set_files(file_list)
		if self.tab_panel.count() == 0:
			self.tab_panel.new_tab()

	def on_message(self, msg, sender, msgtype):
		self.msg_panel.new_message(msg, sender, msgtype)

	def on_error(self, msg):
		self.msg_panel.new_error.emit(msg)
		
	def on_editor_state_changed(self, name, fname, mod_label, operation):
		dash = '' if name == '' else '- '
		self.setWindowTitle(f'{mod_label}{fname} {dash}{EditorApp.win_title}')
		if operation in ['Opened', 'Saved', 'Saved as', 'Reload']:
			self.statusBar.showMessage(f'{operation} {name}', 2000)
		if operation in ['Opened', 'Saved as', 'Reload']:
			self.add_recent_file(fname)
			self.recent_files_changed.emit()

