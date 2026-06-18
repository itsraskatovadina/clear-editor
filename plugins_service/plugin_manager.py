#! /usr/bin/env python3

import importlib
import json
from pathlib import Path
from typing import Optional, Dict

from PyQt5.QtCore import Qt, QObject
from PyQt5.QtWidgets import QAction, QDockWidget, QLabel, QMenu, QToolBar

from plugins_service.plugin_base import PluginBase


class PluginManager(QObject):
	def __init__(self, parent=None, plugins_dir=None):
		super().__init__(parent)
		if plugins_dir:
			self._plugins_dir = Path(plugins_dir)
		else:
			self._plugins_dir = Path(__file__).resolve().parent.parent / "plugins"
		self._available: Dict[str, dict] = {}
		self._active: Dict[str, PluginBase] = {}
		self._active_ui: Dict[str, dict] = {}

	def discover(self):
		self._available.clear()
		if not self._plugins_dir.exists():
			return []

		for folder in self._plugins_dir.iterdir():
			if not folder.is_dir():
				continue
			manifest_path = folder / "manifest.json"
			if not manifest_path.exists():
				continue
			try:
				with open(manifest_path, encoding="utf-8") as f:
					manifest = json.load(f)
				manifest["_path"] = str(folder)
				self._available[manifest["name"]] = manifest
			except (json.JSONDecodeError, KeyError):
				continue

		return list(self._available.values())

	def get_available(self):
		return list(self._available.values())

	def activate(self, name: str, editor) -> Optional[PluginBase]:
		if name in self._active:
			return self._active[name]

		manifest = self._available.get(name)
		if not manifest:
			return None

		folder = Path(manifest["_path"])
		entry = folder / manifest["entry"]

		spec = importlib.util.spec_from_file_location(manifest["name"], entry)
		if not spec or not spec.loader:
			return None

		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)

		plugin_class = getattr(module, manifest["class"])
		plugin = plugin_class()
		plugin.on_load(editor)
		self._active[name] = plugin
		self._setup_ui(name, plugin, editor)
		return plugin

	def _setup_ui(self, name: str, plugin: PluginBase, editor):
		ui_state = {"labels": [], "menu_actions": [], "toolbars": [], "docks": []}

		for fid, field in plugin.status_fields.items():
			label = QLabel(parent=editor.statusBar)
			editor.statusBar.addPermanentWidget(label)
			signal = getattr(plugin, field["signal_name"])
			signal.connect(
				lambda value, t=field["label_template"], l=label:
				l.setText(t.format(value))
			)
			ui_state["labels"].append(label)

		for menu_name, items in plugin.menu_items.items():
			menu = editor.menuBar().findChild(QMenu, menu_name)
			if not menu:
				menu = editor.menuBar().addMenu(menu_name)
				menu.setObjectName(menu_name)
			for item in items:
				action = menu.addAction(item["text"])
				action.triggered.connect(getattr(plugin, item["callback"]))
				ui_state["menu_actions"].append(action)

		if plugin.toolbar_items:
			toolbar = QToolBar(f"plugin_{name}", editor)
			editor.addToolBar(toolbar)
			for item in plugin.toolbar_items:
				action = toolbar.addAction(item["text"])
				action.triggered.connect(getattr(plugin, item["callback"]))
			ui_state["toolbars"].append(toolbar)

		widget = plugin.create_dock_widget(editor)
		if widget is not None:
			dock = QDockWidget(plugin.name, editor)
			dock.setWidget(widget)
			editor.addDockWidget(Qt.BottomDockWidgetArea, dock)
			ui_state["docks"].append(dock)

		self._active_ui[name] = ui_state

	def deactivate(self, name: str):
		ui_state = self._active_ui.pop(name, None)
		if ui_state:
			editor = self.parent()
			for dock in ui_state["docks"]:
				editor.removeDockWidget(dock)
				dock.deleteLater()
			for toolbar in ui_state["toolbars"]:
				editor.removeToolBar(toolbar)
				toolbar.deleteLater()
			for action in ui_state["menu_actions"]:
				action.deleteLater()
			for label in ui_state["labels"]:
				editor.statusBar.removeWidget(label)
				label.deleteLater()
		plugin = self._active.pop(name, None)
		if plugin:
			plugin.on_unload()

	def get_active(self, name: str) -> Optional[PluginBase]:
		return self._active.get(name)

	def get_all_active(self):
		return dict(self._active)
