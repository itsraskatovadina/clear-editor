#! /usr/bin/env python3

import importlib
import json
from pathlib import Path
from typing import Optional, Dict

from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QIcon
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

	def create_action(self, menu, text, callback,
			icon=None, shortcut=None, statustip=None, tooltip=None):
		action = menu.addAction(text)
		if callback:
			action.triggered.connect(callback)
		if icon:
			action.setIcon(QIcon(icon))
		if shortcut:
			action.setShortcut(shortcut)
		if statustip:
			action.setStatusTip(statustip)
		if tooltip:
			action.setToolTip(tooltip)
		return action

	def create_ui_from_actions(self, target, actions, plugin):
		created = []
		for entry in actions:
			kind = entry['kind']
			if kind == 'menu':
				if hasattr(target, 'addMenu'):
					submenu = target.addMenu(entry['text'])
					created.append(('menu', submenu))
				else:
					submenu = target
				if entry.get('content') is not None:
					created.extend(
						self.create_ui_from_actions(submenu, entry['content'], plugin))
			elif kind == 'separator':
				target.addSeparator()
			else:
				cb = None
				if entry.get('callback'):
					cb = getattr(plugin, entry['callback'])
				act = self.create_action(target, entry['text'], cb,
					icon=entry.get('icon'),
					shortcut=entry.get('shortcut'),
					statustip=entry.get('statustip'),
					tooltip=entry.get('tooltip'))
				created.append(('action', act))
		return created

	def _setup_ui(self, name: str, plugin: PluginBase, editor):
		ui_state = {
			"labels": [],
			"menu_ui_objects": [],
			"toolbars": [],
			"docks": [],
		}

		for fid, field in plugin.status_fields.items():
			label = QLabel(parent=editor.statusBar)
			editor.statusBar.addPermanentWidget(label)
			signal = getattr(plugin, field["signal_name"])
			signal.connect(
				lambda value, t=field["label_template"], l=label:
				l.setText(t.format(value))
			)
			ui_state["labels"].append(label)

		for entry in plugin.menu_items:
			if entry.get('kind') == 'menu':
				menu = editor.menuBar().findChild(QMenu, entry['text'])
				if not menu:
					menu = editor.menuBar().addMenu(entry['text'])
					menu.setObjectName(entry['text'])
				if entry.get('content') is not None:
					created = self.create_ui_from_actions(menu, entry['content'], plugin)
					ui_state["menu_ui_objects"].extend(created)

		if plugin.toolbar_items:
			toolbar = QToolBar(f"plugin_{name}", editor)
			editor.addToolBar(toolbar)
			for entry in plugin.toolbar_items:
				if entry.get('kind') == 'menu':
					if entry.get('content') is not None:
						self.create_ui_from_actions(toolbar, entry['content'], plugin)
				else:
					self.create_ui_from_actions(toolbar, [entry], plugin)
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
			for kind, obj in ui_state["menu_ui_objects"]:
				obj.deleteLater()
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
