#! /usr/bin/env python3

from pathlib import Path

from PyQt5.QtWidgets import QMainWindow, QStatusBar, QSplitter, QLabel, QAction
from PyQt5.QtGui import QFont, QIcon, QKeySequence
from PyQt5.QtCore import Qt, QPoint, QSize, pyqtSignal

from core.views.file_tab_view import FileTabView
from core.services.file_tab_srv import FileTabSrv
from core.views.html_editor_widget import HTMLEditor
from core.views.msg_panel_view import MsgPanelView
from core.services.message_srv import MessageSrv
from core.services.config_service import ConfigService, ConfigError
from core.services.theme_service import ThemeService


class EditorApp(QMainWindow):
    win_title = "Text Editor"
    recent_files_changed = pyqtSignal()

    def __init__(self, config_service: ConfigService = None, theme_service: ThemeService = None):
        super().__init__()
        self.setWindowTitle(EditorApp.win_title)
        self.setWindowIcon(QIcon("icons/clear.svg"))
        self.config = None
        self.settings = None
        self.recent_files = []
        self._config_service = config_service
        self.theme = theme_service

        self.file_tab_view = FileTabView(parent=self)
        self.file_tab_srv = FileTabSrv(
            self.file_tab_view, editor_class=HTMLEditor, parent=self
        )
        self.msg_panel = MsgPanelView(parent=self)
        self.msg_srv = MessageSrv(parent=self)
        self.file_tab_srv.message.connect(self.msg_srv.post_message)
        self.msg_srv.display_error.connect(self.msg_panel.append_err)
        self.msg_srv.display_message.connect(self.msg_panel.append_msg)
        self.msg_srv.message_received.connect(self._ensure_msg_panel_visible)
        self.file_tab_srv.editor_state_changed.connect(self.on_editor_state_changed)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.file_tab_view)
        self.splitter.addWidget(self.msg_panel)
        self.splitter.setSizes([500, 100])
        self.setCentralWidget(self.splitter)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.line_label = QLabel(parent=self.statusBar)
        self.statusBar.addPermanentWidget(self.line_label)
        self.file_tab_srv.line_changed.connect(
            lambda line: self.line_label.setText(f"Line: {line}")
        )

    # --- ConfigService delegation ---

    def load_config(self):
        if self._config_service is None:
            self._config_service = ConfigService()
        cs = self._config_service
        self.config = cs.config
        self.settings = cs.settings

        ui_defaults = cs.get_ui_defaults()
        default_pos = ui_defaults.get("geometry/pos", [200, 150])
        default_size = ui_defaults.get("geometry/size", [1500, 900])
        cs.restore_window_geometry(self, default_pos, default_size)

        font_size = cs.restore_font_size(12)
        self.setFont(QFont("SansSerif", font_size))

        self.recent_files = cs.restore_recent_files()

    def closeEvent(self, event):
        if self.settings is not None:
            cs = self._config_service
            cs.save_window_geometry(self)
            font = self.font()
            cs.save_font_size(font.pointSize())
            cs.save_recent_files(self.recent_files)
            open_files = self.file_tab_srv.get_open_files()
            cs.save_open_files(open_files)
            cs.sync()
        self.file_tab_srv.closeEvent(event)
        if not event.isAccepted():
            return
        event.accept()

    def set_tab_panel(self):
        if self.settings is None:
            if self.file_tab_srv.tab_count() == 0:
                self.file_tab_srv.new_tab()
            return
        file_list = self._config_service.restore_open_files()
        if file_list:
            self.file_tab_srv.set_files(file_list)
        if self.file_tab_srv.tab_count() == 0:
            self.file_tab_srv.new_tab()

    # --- Zoom ---

    def zoom_in(self):
        if self.theme:
            self.theme.zoom_in()

    def zoom_out(self):
        if self.theme:
            self.theme.zoom_out()

    def add_recent_file(self, path):
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        if len(self.recent_files) > 10:
            self.recent_files = self.recent_files[:10]

    def action_open_recent_file(self):
        action = self.sender()
        full_path = action.data()
        path = Path(full_path)
        self.file_tab_srv.add_tab(path)

    def action_clear_recent_files(self):
        self.recent_files = []
        self.recent_files_changed.emit()

    def _update_recent_files_menu(self):
        self.recent_files_menu.clear()
        for i, file_path in enumerate(self.recent_files):
            action_text = f"{i + 1}. {file_path}"
            action = QAction(action_text, self)
            action.setData(file_path)
            action.triggered.connect(self.action_open_recent_file)
            self.recent_files_menu.addAction(action)
        if len(self.recent_files) == 0:
            no_files_action = QAction("No recent file", self)
            no_files_action.setEnabled(False)
            self.recent_files_menu.addAction(no_files_action)
        else:
            self.recent_files_menu.addSeparator()
            action = self.recent_files_menu.addAction("Clear recent files")
            action.triggered.connect(self.action_clear_recent_files)

    def current_editor(self):
        return self.file_tab_srv.current_editor()

    def current_file_name(self):
        doc = self.file_tab_srv.current_document()
        return doc.title if doc else ""

    def get_status_bar(self):
        return self.statusBar

    def get_menu_bar(self):
        return self.menuBar()

    def create_menu_bar(self, menu_bar):
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("New", self.file_tab_srv.new_tab)
        file_menu.addAction("Open", self.file_tab_srv.open_file)
        file_menu.addAction("Save", self.file_tab_srv.current_tab_save)
        file_menu.addAction("Save As", self.file_tab_srv.current_tab_save_as)
        file_menu.addAction("Close", self.file_tab_srv.current_tab_close)
        file_menu.addSeparator()
        file_menu.addAction("Reload", self.file_tab_srv.current_tab_reload)
        file_menu.addSeparator()
        file_menu.addAction("Property", self.file_tab_srv.current_tab_view_property)
        file_menu.addSeparator()
        self.recent_files_menu = file_menu.addMenu("Recent files")

        self.recent_files_changed.connect(self._update_recent_files_menu)
        self._update_recent_files_menu()

        settings_menu = menu_bar.addMenu("Settings")
        action_zoom_in = settings_menu.addAction("Zoom In", self.zoom_in)
        action_zoom_in.setShortcut(QKeySequence.ZoomIn)
        action_zoom_out = settings_menu.addAction("Zoom Out", self.zoom_out)
        action_zoom_out.setShortcut(QKeySequence.ZoomOut)
        settings_menu.addSeparator()
        self.plugins_action = settings_menu.addAction("Plugins")

    def on_error(self, msg):
        self.msg_srv.post_message(msg, "System", "error")

    def _ensure_msg_panel_visible(self):
        sizes = self.splitter.sizes()
        if len(sizes) > 1 and sizes[1] == 0:
            self.splitter.setSizes([500, 100])

    def on_editor_state_changed(self, name, fname, mod_label, operation):
        dash = "" if name == "" else "- "
        self.setWindowTitle(f"{mod_label}{fname} {dash}{EditorApp.win_title}")
        if operation in ["Opened", "Saved", "Saved as", "Reload"]:
            self.statusBar.showMessage(f"{operation} {name}", 2000)
        if operation in ["Opened", "Saved as", "Reload"]:
            self.add_recent_file(fname)
            self.recent_files_changed.emit()

    def on_app_focus_changed(self, old, now):
        self.file_tab_srv.on_app_focus_changed(old, now)
