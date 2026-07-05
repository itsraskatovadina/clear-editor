#! /usr/bin/env python3

from plugins_service.models.plugin_registry import PluginRegistry


class _DummyPlugin:
    pass


def test_empty():
    r = PluginRegistry()
    assert r.get_available() == []
    assert r.get_all_active() == {}
    assert r.list_active_names() == []
    assert r.is_available("x") is False
    assert r.is_active("x") is False
    assert r.get_manifest("x") is None
    assert r.get_active("x") is None
    print("  OK empty registry")


def test_register_and_get_available():
    r = PluginRegistry()
    r.register("p1", {"name": "p1", "entry": "main.py"})
    r.register("p2", {"name": "p2", "entry": "main.py"})
    assert r.is_available("p1") is True
    assert r.is_available("p3") is False

    available = r.get_available()
    assert len(available) == 2

    assert r.get_manifest("p1") == {"name": "p1", "entry": "main.py"}
    assert r.get_manifest("p3") is None
    print("  OK register / get_available / get_manifest")


def test_unregister():
    r = PluginRegistry()
    r.register("p1", {"name": "p1"})
    r.unregister("p1")
    assert r.is_available("p1") is False
    assert r.get_available() == []
    print("  OK unregister")


def test_activate_deactivate():
    r = PluginRegistry()
    plugin = _DummyPlugin()
    r.set_active("p1", plugin)

    assert r.is_active("p1") is True
    assert r.get_active("p1") is plugin
    assert r.get_active("p2") is None
    assert r.list_active_names() == ["p1"]

    removed = r.remove_active("p1")
    assert removed is plugin
    assert r.is_active("p1") is False
    print("  OK activate / deactivate")


def test_get_all_active():
    r = PluginRegistry()
    p1, p2 = _DummyPlugin(), _DummyPlugin()
    r.set_active("p1", p1)
    r.set_active("p2", p2)

    all_active = r.get_all_active()
    assert all_active == {"p1": p1, "p2": p2}
    # verify it's a copy
    all_active["p1"] = None
    assert r.get_active("p1") is p1
    print("  OK get_all_active returns copy")


def test_ui_state():
    r = PluginRegistry()
    state = {"labels": [], "toolbars": []}
    r.set_ui_state("p1", state)
    assert r.get_ui_state("p1") is state
    assert r.get_ui_state("p2") is None

    removed = r.remove_ui_state("p1")
    assert removed is state
    assert r.get_ui_state("p1") is None
    print("  OK ui state")


if __name__ == "__main__":
    test_empty()
    test_register_and_get_available()
    test_unregister()
    test_activate_deactivate()
    test_get_all_active()
    test_ui_state()
    print("\nAll PluginRegistry tests passed.")
