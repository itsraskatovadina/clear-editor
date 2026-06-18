#! /usr/bin/env python3

from typing import Optional, Dict, List

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget


class PluginBase(QObject):
	name: str = ""
	description: str = ""

	status_fields: Dict[str, dict] = {}
	menu_items: Dict[str, List[dict]] = {}
	toolbar_items: List[dict] = []

	def on_load(self, editor):
		pass

	def on_unload(self):
		pass

	def create_dock_widget(self, parent=None) -> Optional[QWidget]:
		return None
