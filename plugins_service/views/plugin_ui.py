from typing import Dict, List, Optional

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction,
    QDockWidget,
    QLabel,
    QMenu,
    QToolBar,
    QToolButton,
)

from plugins_service.plugin_base import PluginBase
from plugins_service.models.plugin_registry import PluginRegistry


class PluginUI(QObject):
    variant_tool_submenu = "InstantPopupArrow"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._registry: Optional[PluginRegistry] = None

    def set_registry(self, registry: PluginRegistry):
        self._registry = registry

    def build_status_fields(self, editor, plugin: PluginBase) -> List[QLabel]:
        labels = []
        for field in plugin.status_fields.values():
            label = QLabel(parent=editor.get_status_bar())
            editor.get_status_bar().addPermanentWidget(label)
            signal = getattr(plugin, field["signal_name"])
            signal.connect(
                lambda value, t=field["label_template"], l=label: l.setText(
                    t.format(value)
                )
            )
            labels.append(label)
        return labels

    def build_menu(self, editor, name: str, plugin: PluginBase):
        ui_objects = []
        registered_menus = []
        for entry in plugin.menu_items:
            if entry.get("kind") == "menu":
                text = entry["text"]
                menu = editor.menu_service.get_menu(text)
                if menu:
                    editor.menu_service.register_menu(text, name)
                    registered_menus.append(text)
                items = entry.get("content", [])
                created = self._create_ui_items(menu, items, plugin)
                ui_objects.extend(created)
        return ui_objects, registered_menus

    def build_toolbar(self, editor, name: str, plugin: PluginBase) -> List:
        ui_objects = []
        toolbars = []

        if plugin.toolbar_items:
            toolbar = QToolBar(f"plugin_{name}", editor)
            toolbar.setObjectName(f"plugin_{name}")
            editor.addToolBar(toolbar)
            items = self._resolve_toolbar_items(plugin.toolbar_items, plugin.actions)
            created = self._create_ui_items(toolbar, items, plugin)
            ui_objects.extend(created)
            toolbars.append(toolbar)

        toolbar_widget = plugin.create_toolbar_widget(editor)
        if toolbar_widget is not None:
            toolbar = QToolBar(f"plugin_{name}_toolbar", editor)
            toolbar.setObjectName(f"plugin_{name}_toolbar")
            toolbar.addWidget(toolbar_widget)
            editor.addToolBar(toolbar)
            toolbars.append(toolbar)

        return ui_objects, toolbars

    def build_dock(self, editor, plugin: PluginBase) -> List:
        docks = []
        widget = plugin.create_dock_widget(editor)
        if widget is not None:
            dock = QDockWidget(plugin.name, editor)
            dock.setWidget(widget)
            editor.addDockWidget(plugin.dock_area, dock)
            docks.append(dock)
        return docks

    def build_all(self, editor, name: str, plugin: PluginBase):
        labels = self.build_status_fields(editor, plugin)
        menu_ui, registered_menus = self.build_menu(editor, name, plugin)
        toolbar_ui, toolbars = self.build_toolbar(editor, name, plugin)
        docks = self.build_dock(editor, plugin)
        menu_ui.extend(toolbar_ui)

        state = {
            "labels": labels,
            "menu_ui_objects": menu_ui,
            "registered_menus": registered_menus,
            "toolbars": toolbars,
            "docks": docks,
        }
        if self._registry:
            self._registry.set_ui_state(name, state)
        return state

    def remove_ui(self, editor, name: str, registry: PluginRegistry):
        state = registry.remove_ui_state(name)
        if not state:
            return
        for menu_name in state.get("registered_menus", []):
            editor.menu_service.unregister_menu(menu_name, name)
        for dock in state["docks"]:
            editor.removeDockWidget(dock)
            dock.deleteLater()
        for toolbar in state["toolbars"]:
            editor.removeToolBar(toolbar)
            toolbar.deleteLater()
        for kind, obj in state["menu_ui_objects"]:
            obj.deleteLater()
        for label in state["labels"]:
            editor.get_status_bar().removeWidget(label)
            label.deleteLater()

    def _resolve_toolbar_items(self, toolbar_items, actions):
        result = []
        for entry in toolbar_items:
            if isinstance(entry, str):
                result.append(actions.get(entry, entry))
            elif isinstance(entry, dict) and "ref" in entry:
                action = actions.get(entry["ref"], {}).copy()
                if "label" in entry:
                    action["text"] = entry["label"]
                result.append(action)
            else:
                result.append(entry)
        return result

    def _create_action(self, target, text, callback, icon=None, shortcut=None,
                       statustip=None, tooltip=None):
        action = target.addAction(text)
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

    def _create_ui_items(self, target, items, plugin: PluginBase):
        created = []
        for entry in items:
            if isinstance(entry, dict) and entry.get("kind") == "menu":
                text = entry["text"]
                if hasattr(target, "addMenu"):
                    submenu = target.addMenu(text)
                    created.append(("menu", submenu))
                else:
                    submenu = QMenu(text)
                    btn = QToolButton()
                    btn.setText(text)
                    icon = entry.get("icon")
                    if icon:
                        btn.setIcon(QIcon(icon))
                    btn.setMenu(submenu)
                    btn.setText(text + " \u2193")
                    btn.setPopupMode(QToolButton.InstantPopup)
                    target.addWidget(btn)
                    created.append(("menu_button", btn))
                    created.append(("menu", submenu))
                sub_items = entry.get("content", [])
                created.extend(self._create_ui_items(submenu, sub_items, plugin))

            elif isinstance(entry, dict) and entry.get("kind") == "separator":
                target.addSeparator()

            elif isinstance(entry, str):
                short_text_map = {}
                for act in plugin.actions.values():
                    st = act.get("short_text")
                    if st:
                        short_text_map[act["id"]] = st
                action_cfg = plugin.actions.get(entry)
                if action_cfg:
                    full_entry = dict(action_cfg)
                    if entry in short_text_map and not hasattr(target, "addMenu"):
                        full_entry["text"] = short_text_map[entry]
                    created.extend(self._create_from_cfg(target, full_entry, plugin))
                else:
                    if entry == "---":
                        target.addSeparator()

            elif isinstance(entry, dict) and entry.get("id"):
                created.extend(self._create_from_cfg(target, entry, plugin))

            elif isinstance(entry, dict) and "ref" in entry:
                action_cfg = plugin.actions.get(entry["ref"])
                if action_cfg:
                    full_entry = dict(action_cfg)
                    if "label" in entry:
                        full_entry["text"] = entry["label"]
                    created.extend(self._create_from_cfg(target, full_entry, plugin))

        return created

    def _create_from_cfg(self, target, cfg: dict, plugin: PluginBase):
        cb = None
        if cfg.get("callback"):
            cb = getattr(plugin, cfg["callback"], None)
        act = self._create_action(
            target,
            cfg.get("text", ""),
            cb,
            icon=cfg.get("icon"),
            shortcut=cfg.get("shortcut"),
            statustip=cfg.get("statustip"),
            tooltip=cfg.get("tooltip"),
        )
        return [("action", act)]
