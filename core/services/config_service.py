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
                cfg = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Ошибка парсинга {path}: {e}")
        self.config = cfg
        err = self._validate_plugins_dir()
        if err is not None:
            raise ConfigError(err)
        return cfg

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def get_ui_defaults(self) -> dict:
        return self.config.get("ui_defaults", {})

    def restore_window_geometry(self, window):
        ui_defaults = self.get_ui_defaults()
        default_pos = ui_defaults.get("geometry/pos", [200, 150])
        default_size = ui_defaults.get("geometry/size", [1500, 900])

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

    def _validate_plugins_dir(self) -> Optional[str]:
        pd = self.config.get("plugins_dir")
        if pd is None:
            return "config.json: missing key 'plugins_dir'"
        if not isinstance(pd, str) or not pd.strip():
            return "config.json: 'plugins_dir' must be a non-empty string"
        p = Path(pd)
        if not p.exists():
            return f"config.json: plugins_dir '{pd}' does not exist"
        if not p.is_dir():
            return f"config.json: plugins_dir '{pd}' is not a directory"
        return None

    def _validate_ui_defaults(self, errors: list):
        ui = self.config.get("ui_defaults")
        if ui is None:
            errors.append("config.json: 'ui_defaults' absent")
            return
        if not isinstance(ui, dict):
            errors.append("config.json: 'ui_defaults' must be a dict")
            self.config["ui_defaults"] = {}
            return
        for key in ("geometry/pos", "geometry/size"):
            val = ui.get(key)
            if val is None:
                errors.append(f"config.json: ui_defaults missing '{key}'")
                continue
            if not isinstance(val, list) or len(val) != 2:
                errors.append(f"config.json: ui_defaults '{key}' must be a list of 2 ints")
                del ui[key]
                continue
            if not all(isinstance(v, int) for v in val):
                errors.append(f"config.json: ui_defaults '{key}' must contain integers")
                del ui[key]

    def sync(self):
        self.settings.sync()
