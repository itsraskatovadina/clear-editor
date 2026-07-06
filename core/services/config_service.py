import json
from pathlib import Path
from typing import Any, Dict, Optional

from PyQt5.QtCore import QPoint, QSize, QSettings


class ConfigError(Exception):
    pass


class ConfigService:
    def __init__(self, path: str = "config.json"):
        self.config: Dict[str, Any] = self._load_config(path)
        self.settings: QSettings = QSettings("settings.ini", QSettings.IniFormat)

    def _load_config(self, path: str) -> dict:
        config_path = Path(path)
        if not config_path.exists():
            raise ConfigError(f"Отсутствует файл конфигурации {path}")
        try:
            with open(config_path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Ошибка парсинга {path}: {e}")

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def get_ui_defaults(self) -> dict:
        return self.config.get("ui_defaults", {})

    def restore_window_geometry(self, window, default_pos, default_size):
        pos = self.settings.value("geometry/pos")
        if pos:
            window.move(pos)
        else:
            window.move(QPoint(*default_pos))

        size = self.settings.value("geometry/size")
        if size:
            window.resize(size)
        else:
            window.resize(QSize(*default_size))

    def save_window_geometry(self, window):
        self.settings.setValue("geometry/pos", window.pos())
        self.settings.setValue("geometry/size", window.size())

    def restore_font_size(self, default=12):
        return int(self.settings.value("font_size", default))

    def save_font_size(self, size):
        self.settings.setValue("font_size", size)

    def restore_recent_files(self):
        files = []
        count = self.settings.beginReadArray("recent_files")
        for i in range(count):
            self.settings.setArrayIndex(i)
            f = self.settings.value("f")
            if f:
                files.append(f)
        self.settings.endArray()
        return files

    def save_recent_files(self, files):
        self.settings.beginWriteArray("recent_files")
        for i, f in enumerate(files):
            self.settings.setArrayIndex(i)
            self.settings.setValue("f", f)
        self.settings.endArray()

    def restore_open_files(self):
        files = []
        count = self.settings.beginReadArray("open_files")
        for i in range(count):
            self.settings.setArrayIndex(i)
            f = self.settings.value("f")
            if f:
                files.append(f)
        self.settings.endArray()
        return files

    def save_open_files(self, files):
        self.settings.beginWriteArray("open_files")
        for i, f in enumerate(files):
            self.settings.setArrayIndex(i)
            self.settings.setValue("f", f)
        self.settings.endArray()

    def sync(self):
        self.settings.sync()
