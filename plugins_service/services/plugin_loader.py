import importlib
import json
import sys
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal

from plugins_service.plugin_base import PluginBase
from plugins_service.models.plugin_registry import PluginRegistry


class PluginLoader(QObject):
    plugin_loaded = pyqtSignal(str)
    plugin_error = pyqtSignal(str, str)

    def discover(self, plugins_dir, registry: PluginRegistry):
        path = Path(plugins_dir)
        if not path.exists():
            return

        for folder in path.iterdir():
            if not folder.is_dir():
                continue
            manifest_path = folder / "manifest.json"
            if not manifest_path.exists():
                continue
            try:
                with open(manifest_path, encoding="utf-8") as f:
                    manifest = json.load(f)
                manifest["_path"] = str(folder)
                registry.register(manifest["name"], manifest)
            except (json.JSONDecodeError, KeyError):
                continue

    def load(self, name: str, registry: PluginRegistry) -> Optional[PluginBase]:
        manifest = registry.get_manifest(name)
        if not manifest:
            self.plugin_error.emit(name, "manifest not found")
            return None

        folder = Path(manifest["_path"])
        entry = folder / manifest["entry"]
        sys.path.insert(0, str(folder))
        try:
            spec = importlib.util.spec_from_file_location(name, entry)
            if not spec or not spec.loader:
                self.plugin_error.emit(name, "failed to load spec")
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            self.plugin_error.emit(name, str(e))
            return None
        finally:
            sys.path.remove(str(folder))

        try:
            plugin_class = getattr(module, manifest["class"])
        except AttributeError:
            self.plugin_error.emit(name, f"class {manifest['class']} not found")
            return None

        plugin = plugin_class()
        return plugin

    def deactivate(self, name: str, registry: PluginRegistry):
        plugin = registry.remove_active(name)
        if plugin:
            plugin.on_unload()
