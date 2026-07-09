#! /usr/bin/env python3
#
# Qt addAction(text, callable):
#   если callable — прямая ссылка на метод (obj.method),
#   QAction захватывает её в момент вызова addAction.
#   если callable — лямбда, вызов разрешается при trigger()
#   (т.е. мок нужно ставить до trigger(), а не до addAction).

import sys
from unittest.mock import MagicMock, patch

from PyQt5.QtWidgets import QApplication, QMenuBar

from core.editor_app import EditorApp


app = QApplication(sys.argv)


def test_file_menu_actions():
    config_mock = MagicMock()
    theme_mock = MagicMock()
    editor = EditorApp(config_service=config_mock, theme_service=theme_mock)

    menu_bar = QMenuBar()

    # Patch direct references (captured at addAction time)
    with patch.object(editor.file_tab_srv, "new_tab") as mock_new, \
         patch.object(editor.file_tab_srv, "open_file") as mock_open:
        editor.create_menu_bar(menu_bar)

    file_menu = menu_bar.actions()[0].menu()
    assert file_menu is not None
    assert file_menu.title() == "File"

    actions = file_menu.actions()
    assert actions[0].text() == "New"
    assert actions[1].text() == "Open"
    assert actions[2].text() == "Save"
    assert actions[3].text() == "Save As"
    assert actions[4].text() == "Close"
    assert actions[5].isSeparator()
    assert actions[6].text() == "Reload"
    assert actions[7].isSeparator()
    assert actions[8].text() == "Property"

    actions[0].trigger()
    mock_new.assert_called_once()

    actions[1].trigger()
    mock_open.assert_called_once()

    # Lambda calls resolve at trigger time — patch AFTER menu creation
    with patch.object(editor.file_tab_srv, "current_tab_process") as mock_proc:
        actions[2].trigger()
        mock_proc.assert_called_once_with("save")
        mock_proc.reset_mock()

        actions[3].trigger()
        mock_proc.assert_called_once_with("save_as")
        mock_proc.reset_mock()

        actions[4].trigger()
        mock_proc.assert_called_once_with("close")
        mock_proc.reset_mock()

        actions[6].trigger()
        mock_proc.assert_called_once_with("reload")
        mock_proc.reset_mock()

        actions[8].trigger()
        mock_proc.assert_called_once_with("property")

    print("  OK file_menu_actions")


def test_settings_menu_actions():
    config_mock = MagicMock()
    theme_mock = MagicMock()
    editor = EditorApp(config_service=config_mock, theme_service=theme_mock)

    menu_bar = QMenuBar()

    with patch.object(editor, "zoom_in") as mock_zi, \
         patch.object(editor, "zoom_out") as mock_zo:
        editor.create_menu_bar(menu_bar)

    settings_menu = menu_bar.actions()[1].menu()
    assert settings_menu is not None
    assert settings_menu.title() == "Settings"

    actions = settings_menu.actions()
    assert actions[0].text() == "Zoom In"
    assert actions[1].text() == "Zoom Out"
    assert actions[2].isSeparator()
    assert actions[3].text() == "Plugins"

    actions[0].trigger()
    mock_zi.assert_called_once()

    actions[1].trigger()
    mock_zo.assert_called_once()

    print("  OK settings_menu_actions")


if __name__ == "__main__":
    test_file_menu_actions()
    test_settings_menu_actions()
    print("\nAll EditorApp tests passed.")
