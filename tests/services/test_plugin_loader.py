import sys
import tempfile
from pathlib import Path

from PyQt5.QtWidgets import QApplication

from plugins_service.models.plugin_registry import PluginRegistry
from plugins_service.services.plugin_loader import PluginLoader

app = QApplication(sys.argv)


def _events():
    app.processEvents()


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PLUGINS_DIR = str(PROJECT_ROOT / "plugins")


def test_discover():
    loader = PluginLoader()
    registry = PluginRegistry()
    loader.discover(PLUGINS_DIR, registry)
    available = registry.get_available()
    names = [m["name"] for m in available]
    assert "textprocessing" in names
    assert "htmltools" in names
    assert "iclear" in names
    print("  OK discover finds all plugins")


def test_discover_nonexistent_dir():
    loader = PluginLoader()
    registry = PluginRegistry()
    loader.discover("/nonexistent/path", registry)
    assert registry.get_available() == []
    print("  OK discover nonexistent dir returns empty")


def test_discover_empty_dir():
    with tempfile.TemporaryDirectory() as tmp:
        loader = PluginLoader()
        registry = PluginRegistry()
        loader.discover(tmp, registry)
        assert registry.get_available() == []
    print("  OK discover empty dir returns empty")


def test_load():
    loader = PluginLoader()
    registry = PluginRegistry()
    loader.discover(PLUGINS_DIR, registry)
    plugin = loader.load("textprocessing", registry)
    _events()
    assert plugin is not None
    assert plugin.name == "textprocessing"
    print("  OK load plugin")


def test_load_invalid_name():
    loader = PluginLoader()
    registry = PluginRegistry()
    errors = []

    loader.plugin_error.connect(lambda name, err: errors.append((name, err)))
    plugin = loader.load("NonExistent", registry)
    _events()
    assert plugin is None
    assert len(errors) == 1
    assert errors[0][0] == "NonExistent"
    print("  OK load invalid name emits error signal")


def test_deactivate():
    loader = PluginLoader()
    registry = PluginRegistry()
    loader.discover(PLUGINS_DIR, registry)
    plugin = loader.load("textprocessing", registry)
    assert plugin is not None
    registry.set_active("textprocessing", plugin)
    assert registry.is_active("textprocessing") is True

    loader.deactivate("textprocessing", registry)
    assert registry.is_active("textprocessing") is False
    assert registry.get_active("textprocessing") is None
    print("  OK deactivate")


if __name__ == "__main__":
    test_discover()
    test_discover_nonexistent_dir()
    test_discover_empty_dir()
    test_load()
    test_load_invalid_name()
    test_deactivate()
    print("\nAll PluginLoader tests passed.")
