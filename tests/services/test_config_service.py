#! /usr/bin/env python3

import json
import sys
import tempfile
from pathlib import Path

from core.services.config_service import ConfigService, ConfigError


def test_missing_config_raises():
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "nonexistent.json")
        try:
            ConfigService(path)
            assert False, "expected ConfigError"
        except ConfigError as e:
            assert "Отсутствует" in str(e)
            print("  OK missing config → ConfigError")


def test_broken_json_raises():
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "config.json"
        config_path.write_text("{bad json}", encoding="utf-8")
        try:
            ConfigService(str(config_path))
            assert False, "expected ConfigError"
        except ConfigError as e:
            assert "Ошибка парсинга" in str(e)
            print("  OK broken JSON → ConfigError")


def test_valid_config_no_errors():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "plugins").mkdir()
        config_path = Path(tmp) / "config.json"
        config_path.write_text(json.dumps({
            "plugins_dir": "plugins",
            "ui_defaults": {"geometry/pos": [100, 200], "geometry/size": [800, 600]}
        }), encoding="utf-8")
        cs = ConfigService(str(config_path))
        errors = []
        cs._validate_ui_defaults(errors)
        assert errors == [], f"expected no errors, got: {errors}"
        print("  OK valid config → no errors")


def test_validate_missing_plugins_dir():
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "config.json"
        config_path.write_text(json.dumps({"ui_defaults": {}}), encoding="utf-8")
        try:
            ConfigService(str(config_path))
            assert False, "expected ConfigError"
        except ConfigError as e:
            assert "plugins_dir" in str(e)
            print("  OK missing plugins_dir → ConfigError")


def test_validate_plugins_dir_not_exists():
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "config.json"
        config_path.write_text(json.dumps({"plugins_dir": "no_such_dir"}), encoding="utf-8")
        try:
            ConfigService(str(config_path))
            assert False, "expected ConfigError"
        except ConfigError as e:
            assert "does not exist" in str(e)
            print("  OK plugins_dir not exists → ConfigError")


def test_validate_plugins_dir_is_file():
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "config.json"
        config_path.write_text(json.dumps({"plugins_dir": "config.json"}), encoding="utf-8")
        try:
            ConfigService(str(config_path))
            assert False, "expected ConfigError"
        except ConfigError as e:
            assert "not a directory" in str(e)
            print("  OK plugins_dir is file → ConfigError")


def test_validate_ui_defaults_absent():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "plugins").mkdir()
        config_path = Path(tmp) / "config.json"
        config_path.write_text(json.dumps({"plugins_dir": "plugins"}), encoding="utf-8")
        cs = ConfigService(str(config_path))
        errors = []
        cs._validate_ui_defaults(errors)
        assert any("ui_defaults" in e and "absent" in e for e in errors), f"expected ui_defaults absent error, got: {errors}"
        print("  OK missing ui_defaults → error")


def test_validate_ui_defaults_bad_type():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "plugins").mkdir()
        config_path = Path(tmp) / "config.json"
        config_path.write_text(json.dumps({
            "plugins_dir": "plugins",
            "ui_defaults": "not_a_dict"
        }), encoding="utf-8")
        cs = ConfigService(str(config_path))
        errors = []
        cs._validate_ui_defaults(errors)
        assert any("ui_defaults" in e and "dict" in e for e in errors), f"expected ui_defaults type error, got: {errors}"
        print("  OK ui_defaults bad type → error")


def test_validate_ui_defaults_geometry_pos_not_list():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "plugins").mkdir()
        config_path = Path(tmp) / "config.json"
        config_path.write_text(json.dumps({
            "plugins_dir": "plugins",
            "ui_defaults": {"geometry/pos": "100,200", "geometry/size": [800, 600]}
        }), encoding="utf-8")
        cs = ConfigService(str(config_path))
        errors = []
        cs._validate_ui_defaults(errors)
        assert any("geometry/pos" in e for e in errors), f"expected geometry/pos error, got: {errors}"
        print("  OK ui_defaults geometry/pos not list → error")


def test_validate_ui_defaults_geometry_pos_wrong_len():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "plugins").mkdir()
        config_path = Path(tmp) / "config.json"
        config_path.write_text(json.dumps({
            "plugins_dir": "plugins",
            "ui_defaults": {"geometry/pos": [100], "geometry/size": [800, 600]}
        }), encoding="utf-8")
        cs = ConfigService(str(config_path))
        errors = []
        cs._validate_ui_defaults(errors)
        assert any("geometry/pos" in e for e in errors), f"expected geometry/pos len error, got: {errors}"
        print("  OK ui_defaults geometry/pos wrong len → error")


def test_validate_ui_defaults_geometry_pos_non_int():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "plugins").mkdir()
        config_path = Path(tmp) / "config.json"
        config_path.write_text(json.dumps({
            "plugins_dir": "plugins",
            "ui_defaults": {"geometry/pos": [100, "200"], "geometry/size": [800, 600]}
        }), encoding="utf-8")
        cs = ConfigService(str(config_path))
        errors = []
        cs._validate_ui_defaults(errors)
        assert any("geometry/pos" in e for e in errors), f"expected geometry/pos int error, got: {errors}"
        print("  OK ui_defaults geometry/pos non-int → error")


if __name__ == "__main__":
    test_missing_config_raises()
    test_broken_json_raises()
    test_valid_config_no_errors()
    test_validate_missing_plugins_dir()
    test_validate_plugins_dir_not_exists()
    test_validate_plugins_dir_is_file()
    test_validate_ui_defaults_absent()
    test_validate_ui_defaults_bad_type()
    test_validate_ui_defaults_geometry_pos_not_list()
    test_validate_ui_defaults_geometry_pos_wrong_len()
    test_validate_ui_defaults_geometry_pos_non_int()
    print("\nAll ConfigService tests passed.")
