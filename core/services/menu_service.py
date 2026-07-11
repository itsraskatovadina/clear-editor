from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMenu, QMenuBar


_TEMPLATE = [
    {"name": "File", "always_visible": True},
    {"name": "Edit", "always_visible": False},
    {"name": "Tools", "always_visible": False},
    {"name": "Settings", "always_visible": True},
]


class MenuService(QObject):
    menu_registered = pyqtSignal(str)
    menu_unregistered = pyqtSignal(str)

    def __init__(self, menu_bar: QMenuBar, parent=None):
        super().__init__(parent)
        self._menu_bar = menu_bar
        self._menus = {}
        self._references = {}
        self._create_template()

    def _create_template(self):
        for entry in _TEMPLATE:
            name = entry["name"]
            menu = self._menu_bar.addMenu(name)
            menu.setObjectName(name)
            self._menus[name] = menu
            self._references[name] = set()
            if not entry["always_visible"]:
                menu.menuAction().setVisible(False)

    def get_menu(self, menu_name: str) -> QMenu:
        return self._menus.get(menu_name)

    def register_menu(self, menu_name: str, plugin_name: str):
        refs = self._references.get(menu_name)
        if refs is None:
            refs = set()
            self._references[menu_name] = refs
        was_empty = len(refs) == 0
        refs.add(plugin_name)
        if was_empty:
            menu = self._menus.get(menu_name)
            if menu:
                menu.menuAction().setVisible(True)
            self.menu_registered.emit(menu_name)

    def unregister_menu(self, menu_name: str, plugin_name: str):
        refs = self._references.get(menu_name)
        if refs is None:
            return
        refs.discard(plugin_name)
        if len(refs) == 0:
            menu = self._menus.get(menu_name)
            if menu and not self._is_always_visible(menu_name):
                menu.menuAction().setVisible(False)
            self.menu_unregistered.emit(menu_name)

    def _is_always_visible(self, menu_name: str) -> bool:
        for entry in _TEMPLATE:
            if entry["name"] == menu_name:
                return entry["always_visible"]
        return False
