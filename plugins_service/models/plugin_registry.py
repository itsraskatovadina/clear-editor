from typing import Dict, List, Optional

from plugins_service.plugin_base import PluginBase


class PluginRegistry:
    def __init__(self):
        self._available: Dict[str, dict] = {}
        self._active: Dict[str, PluginBase] = {}
        self._active_ui: Dict[str, dict] = {}

    # --- available ---

    def register(self, name: str, manifest: dict) -> None:
        self._available[name] = manifest

    def unregister(self, name: str) -> None:
        self._available.pop(name, None)

    def is_available(self, name: str) -> bool:
        return name in self._available

    def get_available(self) -> List[dict]:
        return list(self._available.values())

    def get_manifest(self, name: str) -> Optional[dict]:
        return self._available.get(name)

    # --- active ---

    def set_active(self, name: str, plugin: PluginBase) -> None:
        self._active[name] = plugin

    def remove_active(self, name: str) -> Optional[PluginBase]:
        return self._active.pop(name, None)

    def is_active(self, name: str) -> bool:
        return name in self._active

    def get_active(self, name: str) -> Optional[PluginBase]:
        return self._active.get(name)

    def get_all_active(self) -> Dict[str, PluginBase]:
        return dict(self._active)

    def list_active_names(self) -> List[str]:
        return list(self._active.keys())

    # --- ui state ---

    def set_ui_state(self, name: str, state: dict) -> None:
        self._active_ui[name] = state

    def get_ui_state(self, name: str) -> Optional[dict]:
        return self._active_ui.get(name)

    def remove_ui_state(self, name: str) -> Optional[dict]:
        return self._active_ui.pop(name, None)
