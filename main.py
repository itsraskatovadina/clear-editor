#! /usr/bin/env python3

import sys
import traceback

from PyQt5.QtWidgets import QApplication

from plugins_service.plugin_manager import PluginManager
from plugins_service.plugin_widget import PluginWidget
from plugins_service.models.plugin_registry import PluginRegistry
from plugins_service.services.plugin_loader import PluginLoader
from plugins_service.views.plugin_ui import PluginUI
from core.editor_app import EditorApp, ConfigError
from core.services.message_srv import ErrorHandler
from core.services.theme_service import ThemeService


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ClearEditor")

    editor_app = EditorApp()
    editor_app.theme = ThemeService(target=editor_app)
    try:
        editor_app.load_config()
    except ConfigError as e:
        print(e)
        sys.exit(1)

    editor_app.set_tab_panel()

    registry = PluginRegistry()
    loader = PluginLoader()
    ui = PluginUI()
    plugin_manager = PluginManager(
        registry, loader, ui,
        parent=editor_app, plugins_dir=editor_app.config["plugins_dir"]
    )
    settings = editor_app.settings

    original_stderr = sys.stderr
    sys.stderr = ErrorHandler(editor_app.on_error)

    def excepthook(exc_type, exc_value, exc_tb):
        msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        original_stderr.write(msg)
        editor_app.on_error(msg)

    sys.excepthook = excepthook
    
    plugin_manager.discover()

    def open_plugin_settings():
        active_before = plugin_manager.get_all_active()
        selected = settings.value("active_plugins", [])
        if selected is None:
            selected = []
        elif isinstance(selected, str):
            selected = [selected]

        dialog = PluginWidget(
            registry,
            set(selected),
            editor_app,
        )
        if dialog.exec() == PluginWidget.Accepted:
            new_selection = dialog.get_selected_names()
            settings.setValue("active_plugins", list(new_selection))

            for name in active_before:
                if name not in new_selection:
                    plugin_manager.deactivate(name)

            for name in new_selection:
                if name not in active_before:
                    plugin_manager.activate(name, editor_app)

    menu_bar = editor_app.menuBar()
    editor_app.create_menu_bar(menu_bar)
    editor_app.plugins_action.triggered.connect(open_plugin_settings)

    loaded = settings.value("active_plugins", [])
    if loaded is None:
        loaded = []
    elif isinstance(loaded, str):
        loaded = [loaded]
    for name in loaded:
        plugin_manager.activate(name, editor_app)

    app.focusChanged.connect(editor_app.on_app_focus_changed)

    editor_app.show()
    app_exit_code = app.exec_()
    sys.stderr = original_stderr
    sys.exit(app_exit_code)


if __name__ == "__main__":
    main()
