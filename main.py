#! /usr/bin/env python3

import sys
import traceback

from PyQt5.QtWidgets import QApplication, QAction

from plugins_service.plugin_manager import PluginManager
from plugins_service.plugin_widget import PluginWidget
from core.editor_app import EditorApp, ConfigError
from core.msg_panel import ErrorHandler


def main():
	app = QApplication(sys.argv)
	app.setApplicationName("ClearEditor")

	editor_app = EditorApp()
	try:
		editor_app.load_config()
	except ConfigError as e:
		print(e)
		sys.exit(1)

	editor_app.set_tab_panel()

	plugin_manager = PluginManager(
		editor_app,
		plugins_dir=editor_app.config["plugins_dir"]
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
			plugin_manager.get_available(),
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

	def create_menu_bar(menu_bar):
		file_menu = menu_bar.addMenu("File")
		file_menu.addAction('New', editor_app.tab_panel.new_tab)
		file_menu.addAction('Open', editor_app.tab_panel.open_file)
		file_menu.addAction('Save', editor_app.tab_panel.current_tab_save)
		file_menu.addAction('Save As', editor_app.tab_panel.current_tab_save_as)
		file_menu.addAction('Close', editor_app.tab_panel.current_tab_close)
		file_menu.addSeparator()
		file_menu.addAction('Reload', editor_app.tab_panel.current_tab_reload)
		file_menu.addSeparator()
		file_menu.addAction('Property', editor_app.tab_panel.current_tab_view_property)
		file_menu.addSeparator()
		editor_app.recent_files_menu = file_menu.addMenu("Recent files")

	def update_recent_files_menu():
		editor_app.recent_files_menu.clear()
		for i, file_path in enumerate(editor_app.recent_files):
			action_text = f"{i+1}. {file_path}"
			action = QAction(action_text, editor_app)
			action.setData(file_path)
			action.triggered.connect(editor_app.action_open_recent_file)
			editor_app.recent_files_menu.addAction(action)
		if len(editor_app.recent_files) == 0:
			no_files_action = QAction("No recent file", editor_app)
			no_files_action.setEnabled(False)
			editor_app.recent_files_menu.addAction(no_files_action)
		else:
			editor_app.recent_files_menu.addSeparator()
			action = editor_app.recent_files_menu.addAction("Clear recent files")
			action.triggered.connect(editor_app.action_clear_recent_files)

	menu_bar = editor_app.menuBar()
	create_menu_bar(menu_bar)
	editor_app.recent_files_changed.connect(update_recent_files_menu)
	update_recent_files_menu()

	loaded = settings.value("active_plugins", [])
	if isinstance(loaded, str):
		loaded = [loaded]
	for name in loaded:
		plugin_manager.activate(name, editor_app)

	settings_menu = menu_bar.addMenu("Settings")
	settings_menu.addAction("Zoom In", editor_app.zoom_in)
	settings_menu.addAction("Zoom Out", editor_app.zoom_out)
	settings_menu.addSeparator()
	settings_menu.addAction("Plugins", open_plugin_settings)

	app.focusChanged.connect(editor_app.tab_panel.on_app_focus_changed)

	editor_app.show()
	app_exit_code = app.exec_()
	sys.stderr = original_stderr
	sys.exit(app_exit_code)


if __name__ == "__main__":
	main()
