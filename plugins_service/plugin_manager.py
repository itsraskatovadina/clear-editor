from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QObject

from plugins_service.plugin_base import PluginBase
from plugins_service.models.plugin_registry import PluginRegistry
from plugins_service.services.plugin_loader import PluginLoader
from plugins_service.views.plugin_ui import PluginUI


class PluginManager(QObject):
    def __init__(
        self,
        registry: PluginRegistry,
        loader: PluginLoader,
        ui: PluginUI,
        parent=None,
        plugins_dir=None,
    ):
        super().__init__(parent)
        self._registry = registry
        self._loader = loader
        self._ui = ui
        self._ui.set_registry(registry)

        if plugins_dir:
            self._plugins_dir = Path(plugins_dir)
        else:
            self._plugins_dir = Path(__file__).resolve().parent.parent / "plugins"

    def discover(self):
        self._loader.discover(str(self._plugins_dir), self._registry)
        return self._registry.get_available()

    def get_available(self):
        return self._registry.get_available()

    def activate(self, name: str, editor) -> Optional[PluginBase]:
        if self._registry.is_active(name):
            return self._registry.get_active(name)

        plugin = self._loader.load(name, self._registry)
        if not plugin:
            return None
        plugin.on_load(editor)
        self._registry.set_active(name, plugin)
        self._ui.build_all(editor, name, plugin)
        return plugin

    def deactivate(self, name: str):
        editor = self.parent()
        self._ui.remove_ui(editor, name, self._registry)
        self._loader.deactivate(name, self._registry)

    def get_active(self, name: str) -> Optional[PluginBase]:
        return self._registry.get_active(name)

    def get_all_active(self):
        return self._registry.get_all_active()
