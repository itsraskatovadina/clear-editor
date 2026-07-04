#! /usr/bin/env python3

from pathlib import Path

from core.models.file_tab_models import FileTabModel


def test_empty():
    m = FileTabModel()
    assert m.count == 0
    assert m.current() is None
    assert m.at(0) is None
    assert m.current_index == -1
    print("  OK empty model")


def test_add():
    m = FileTabModel()
    d = m.add()
    assert m.count == 1
    assert d.file_path is None
    assert m.at(0) is d
    assert m.current() is None
    print("  OK add untitled")


def test_add_with_path():
    m = FileTabModel()
    d = m.add(Path("/a/b.txt"))
    assert d.file_path == Path("/a/b.txt")
    assert d.title == "b.txt"
    print("  OK add with path")


def test_set_and_get_current():
    m = FileTabModel()
    d0 = m.add()
    d1 = m.add()
    d2 = m.add()
    assert m.current_index == -1

    m.set_current(1)
    assert m.current_index == 1
    assert m.current() is d1

    m.set_current(0)
    assert m.current() is d0
    print("  OK set/get current")


def test_remove():
    m = FileTabModel()
    d0 = m.add()
    d1 = m.add()

    m.set_current(1)
    assert m.current() is d1

    m.remove(1)
    assert m.count == 1
    assert m.at(1) is None
    assert m.current_index == 0

    m.remove(0)
    assert m.count == 0
    assert m.current_index == -1
    assert m.current() is None
    print("  OK remove")


def test_remove_updates_current():
    m = FileTabModel()
    d0 = m.add()
    d1 = m.add()
    d2 = m.add()

    m.set_current(2)
    m.remove(2)
    assert m.current_index == 1

    m.set_current(0)
    m.remove(0)
    assert m.current_index == 0
    print("  OK remove updates current")


def test_add_returns_distinct():
    m = FileTabModel()
    a = m.add()
    b = m.add()
    assert a is not b
    assert a != b
    print("  OK distinct documents")


def test_remove_invalid_index():
    m = FileTabModel()
    assert m.remove(0) is False
    assert m.remove(-1) is False
    m.add()
    assert m.remove(1) is False
    print("  OK remove invalid index")


if __name__ == "__main__":
    test_empty()
    test_add()
    test_add_with_path()
    test_set_and_get_current()
    test_remove()
    test_remove_updates_current()
    test_add_returns_distinct()
    test_remove_invalid_index()
    print("\nAll FileTabModel tests passed.")
