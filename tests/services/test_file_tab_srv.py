#! /usr/bin/env python3

import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog

from core.views.file_tab_view import FileTabView
from core.services.file_tab_srv import FileTabSrv


app = QApplication(sys.argv)


def _events():
    app.processEvents()


def _modify_current(srv, text):
    """Simulate user editing — modify document content and set modified flag."""
    doc = srv.current_document()
    doc._qdoc.setPlainText(text)
    _events()


def test_new_tab():
    view = FileTabView()
    srv = FileTabSrv(view)
    assert srv.tab_count() == 0
    srv.new_tab()
    _events()
    assert srv.tab_count() == 1
    assert srv.current_document() is not None
    srv.new_tab()
    _events()
    assert srv.tab_count() == 2
    print("  OK new_tab")


def test_add_tab_with_file():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "test.txt"
        p.write_text("hello", encoding="utf-8")

        view = FileTabView()
        srv = FileTabSrv(view)
        assert srv.add_tab(p) is True
        _events()
        assert srv.tab_count() == 1
        doc = srv.current_document()
        assert doc.file_path == p
        assert doc.content == "hello"
        doc2 = srv.current_document()
        assert doc2 is doc
        print("  OK add_tab with file")


def test_add_tab_duplicate():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "test.txt"
        p.write_text("hello")

        view = FileTabView()
        srv = FileTabSrv(view)
        srv.add_tab(p)
        _events()
        assert srv.add_tab(p) is True
        assert srv.tab_count() == 1
        print("  OK add_tab duplicate")


def test_save_tab():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "test.txt"
        p.write_text("original")

        view = FileTabView()
        srv = FileTabSrv(view)
        srv.add_tab(p)
        _events()

        _modify_current(srv, "modified")

        srv.current_tab_process("save")
        _events()
        assert p.read_text(encoding="utf-8") == "modified"
        doc = srv.current_document()
        assert doc.modified is False
        print("  OK save_tab")


def test_save_as_tab():
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src.txt"
        dst = Path(tmp) / "dst.txt"
        src.write_text("original")

        view = FileTabView()
        srv = FileTabSrv(view)
        srv.add_tab(src)
        _events()

        _modify_current(srv, "saved as")

        def mock_saveas(*a, **kw):
            return (str(dst), "")

        with patch.object(QFileDialog, "getSaveFileName", mock_saveas):
            srv.current_tab_process("save_as")
            _events()

        assert dst.read_text(encoding="utf-8") == "saved as"
        doc = srv.current_document()
        assert doc.file_path == dst
        print("  OK save_as tab")


def test_close_tab_without_modification():
    view = FileTabView()
    srv = FileTabSrv(view)
    srv.new_tab()
    srv.new_tab()
    _events()

    assert srv.tab_count() == 2
    srv.current_tab_process("close")
    _events()
    assert srv.tab_count() == 1
    print("  OK close_tab without modification")


def test_close_with_modification_save():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "test.txt"
        p.write_text("original")

        view = FileTabView()
        srv = FileTabSrv(view)
        srv.add_tab(p)
        _events()

        _modify_current(srv, "modified")

        with patch.object(QMessageBox, "question", return_value=QMessageBox.Save):
            result = srv.close_tab(0, close_last_tab=True)
            _events()

        assert result is True
        assert srv.tab_count() == 0
        assert p.read_text(encoding="utf-8") == "modified"
        print("  OK close with modification → Save")


def test_close_with_modification_ignore():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "test.txt"
        p.write_text("original")

        view = FileTabView()
        srv = FileTabSrv(view)
        srv.add_tab(p)
        _events()

        _modify_current(srv, "modified")

        with patch.object(QMessageBox, "question", return_value=QMessageBox.Ignore):
            result = srv.close_tab(0, close_last_tab=True)
            _events()

        assert result is True
        assert srv.tab_count() == 0
        assert p.read_text(encoding="utf-8") == "original"
        print("  OK close with modification → Ignore")


def test_close_with_modification_cancel():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "test.txt"
        p.write_text("original")

        view = FileTabView()
        srv = FileTabSrv(view)
        srv.add_tab(p)
        _events()

        _modify_current(srv, "modified")

        with patch.object(QMessageBox, "question", return_value=QMessageBox.Cancel):
            result = srv.close_tab(0, close_last_tab=True)
            _events()

        assert result is False
        assert srv.tab_count() == 1
        assert p.read_text(encoding="utf-8") == "original"
        print("  OK close with modification → Cancel")


def test_open_file():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "opened.txt"
        p.write_text("opened from dialog")

        def mock_open(*a, **kw):
            return (str(p), "")

        with patch.object(QFileDialog, "getOpenFileName", mock_open):
            view = FileTabView()
            srv = FileTabSrv(view)
            srv.open_file()
            _events()

        assert srv.tab_count() == 1
        doc = srv.current_document()
        assert doc.file_path == p
        assert doc.content == "opened from dialog"
        print("  OK open_file")


def test_tab_moved():
    with tempfile.TemporaryDirectory() as tmp:
        a = Path(tmp) / "a.txt"
        b = Path(tmp) / "b.txt"
        a.write_text("content a")
        b.write_text("content b")

        view = FileTabView()
        srv = FileTabSrv(view)
        srv.add_tab(a)
        srv.add_tab(b)
        _events()

        assert srv.tab_count() == 2

        doc0 = srv._model.at(0)
        doc1 = srv._model.at(1)
        assert doc0.file_path == a
        assert doc1.file_path == b
        assert doc0.content == "content a"
        assert doc1.content == "content b"

        tab_bar = view.tabBar()
        tab_bar.moveTab(0, 1)
        _events()

        assert srv._model.at(1) is doc0
        assert srv._model.at(0) is doc1
        print("  OK tab_moved")


def test_reload_tab():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "reload.txt"
        p.write_text("version 1")

        view = FileTabView()
        srv = FileTabSrv(view)
        srv.add_tab(p)
        _events()

        _modify_current(srv, "user edit")

        p.write_text("version 2")

        srv.current_tab_process("reload")
        _events()

        doc = srv.current_document()
        assert doc.content == "version 2"
        print("  OK reload_tab")


def test_session():
    with tempfile.TemporaryDirectory() as tmp:
        a = Path(tmp) / "a.txt"
        b = Path(tmp) / "b.txt"
        a.write_text("a")
        b.write_text("b")

        view = FileTabView()
        srv = FileTabSrv(view)
        srv.add_tab(a)
        srv.add_tab(b)

        files = srv.get_open_files()
        assert files == [str(a), str(b)]

        view2 = FileTabView()
        srv2 = FileTabSrv(view2)
        count = srv2.set_files(files)
        _events()
        assert count == 2
        print("  OK session")


if __name__ == "__main__":
    test_new_tab()
    test_add_tab_with_file()
    test_add_tab_duplicate()
    test_save_tab()
    test_save_as_tab()
    test_close_tab_without_modification()
    test_close_with_modification_save()
    test_close_with_modification_ignore()
    test_close_with_modification_cancel()
    test_open_file()
    test_tab_moved()
    test_reload_tab()
    test_session()
    print("\nAll FileTabSrv tests passed.")
