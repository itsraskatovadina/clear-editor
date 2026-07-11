import sys

from PyQt5.QtWidgets import QApplication, QMenuBar

from core.services.menu_service import MenuService


app = QApplication(sys.argv)


def test_template_creation():
    menu_bar = QMenuBar()
    svc = MenuService(menu_bar)

    file_menu = svc.get_menu("File")
    assert file_menu is not None
    assert file_menu.title() == "File"
    assert file_menu.menuAction().isVisible()

    edit_menu = svc.get_menu("Edit")
    assert edit_menu is not None
    assert not edit_menu.menuAction().isVisible()

    tools_menu = svc.get_menu("Tools")
    assert tools_menu is not None
    assert not tools_menu.menuAction().isVisible()

    settings_menu = svc.get_menu("Settings")
    assert settings_menu is not None
    assert settings_menu.menuAction().isVisible()

    print("  OK template_creation")


def test_register_shows_menu():
    menu_bar = QMenuBar()
    svc = MenuService(menu_bar)

    edit_menu = svc.get_menu("Edit")
    assert not edit_menu.menuAction().isVisible()

    svc.register_menu("Edit", "textprocessing")
    assert edit_menu.menuAction().isVisible()

    print("  OK register_shows_menu")


def test_unregister_hides_menu():
    menu_bar = QMenuBar()
    svc = MenuService(menu_bar)

    svc.register_menu("Edit", "textprocessing")
    svc.register_menu("Edit", "htmltools")

    svc.unregister_menu("Edit", "textprocessing")
    edit_menu = svc.get_menu("Edit")
    assert edit_menu.menuAction().isVisible()

    svc.unregister_menu("Edit", "htmltools")
    assert not edit_menu.menuAction().isVisible()

    print("  OK unregister_hides_menu")


def test_always_visible_not_hidden():
    menu_bar = QMenuBar()
    svc = MenuService(menu_bar)

    svc.register_menu("File", "some_plugin")
    svc.unregister_menu("File", "some_plugin")
    file_menu = svc.get_menu("File")
    assert file_menu.menuAction().isVisible()

    print("  OK always_visible_not_hidden")


def test_get_nonexistent_menu():
    menu_bar = QMenuBar()
    svc = MenuService(menu_bar)

    assert svc.get_menu("Nonexistent") is None

    print("  OK get_nonexistent_menu")


def test_signals():
    menu_bar = QMenuBar()
    svc = MenuService(menu_bar)

    registered = []
    unregistered = []
    svc.menu_registered.connect(lambda name: registered.append(name))
    svc.menu_unregistered.connect(lambda name: unregistered.append(name))

    svc.register_menu("Edit", "plugin_a")
    svc.register_menu("Edit", "plugin_b")
    svc.unregister_menu("Edit", "plugin_a")
    svc.unregister_menu("Edit", "plugin_b")

    assert registered == ["Edit"]
    assert unregistered == ["Edit"]

    print("  OK signals")


if __name__ == "__main__":
    test_template_creation()
    test_register_shows_menu()
    test_unregister_hides_menu()
    test_always_visible_not_hidden()
    test_get_nonexistent_menu()
    test_signals()
    print("\nAll MenuService tests passed.")
