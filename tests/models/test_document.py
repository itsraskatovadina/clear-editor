#! /usr/bin/env python3

import sys
import tempfile
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QTextDocument

from core.models.file_tab_models import Document


app = QApplication(sys.argv)


def test_ctor():
    d = Document()
    assert d.file_path is None
    assert d.encoding == "utf-8"
    assert d.title == "untitled"
    assert d.full_title == "untitled"
    assert d.modified is False
    assert d.content == ""
    print("  OK ctor")


def test_ctor_with_path():
    p = Path("/foo/bar.txt")
    d = Document(file_path=p)
    assert d.file_path == p
    assert d.title == "bar.txt"
    assert d.full_title == "/foo/bar.txt"
    print("  OK ctor with path")


def test_modified():
    d = Document()
    qdoc = QTextDocument()
    d.bind(qdoc)
    assert d.modified is False
    qdoc.setPlainText("hello")
    assert d.modified is True
    qdoc.setModified(False)
    assert d.modified is False
    d.modified = True
    assert d.modified is True
    d.modified = False
    assert d.modified is False
    print("  OK modified")


def test_content():
    d = Document()
    qdoc = QTextDocument()
    d.bind(qdoc)
    assert d.content == ""
    qdoc.setPlainText("abc")
    assert d.content == "abc"
    print("  OK content")


def test_load_save():
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src.txt"
        src.write_text("hello world", encoding="utf-8")

        d = Document(file_path=src)
        qdoc = QTextDocument()
        d.bind(qdoc)

        text = d.load()
        assert text == "hello world"
        print("  OK load")

        qdoc.setPlainText("overwritten")
        d.save()
        assert src.read_text(encoding="utf-8") == "overwritten"
        assert d.modified is False
        print("  OK save")


def test_save_as():
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src.txt"
        dst = Path(tmp) / "dst.txt"
        src.write_text("source", encoding="utf-8")

        d = Document(file_path=src)
        qdoc = QTextDocument()
        d.bind(qdoc)
        d.load()

        qdoc.setPlainText("target content")
        d.save_as(dst)
        assert dst.read_text(encoding="utf-8") == "target content"
        assert d.file_path == dst
        assert d.modified is False
        print("  OK save_as")


def test_external_modified():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "f.txt"
        p.write_text("v1", encoding="utf-8")

        d = Document(file_path=p)
        qdoc = QTextDocument()
        d.bind(qdoc)
        d.load()
        assert d.is_externally_modified() is False

        import time

        time.sleep(0.1)
        p.write_text("v2", encoding="utf-8")
        assert d.is_externally_modified() is True

        d.load()
        assert d.is_externally_modified() is False
        print("  OK external modified")


def test_external_modified_no_file():
    d = Document()
    assert d.is_externally_modified() is False
    d.file_path = Path("/nonexistent/file.txt")
    assert d.is_externally_modified() is False
    print("  OK external modified no file")


if __name__ == "__main__":
    test_ctor()
    test_ctor_with_path()
    test_modified()
    test_content()
    test_load_save()
    test_save_as()
    test_external_modified()
    test_external_modified_no_file()
    print("\nAll Document tests passed.")
