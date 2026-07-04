#! /usr/bin/env python3

import datetime

from core.models.message_model import Message


def test_default_values():
    m = Message(text="hello")
    assert m.text == "hello"
    assert m.sender == ""
    assert m.msg_type == "info"
    assert isinstance(m.timestamp, datetime.datetime)
    print("  OK default values")


def test_custom_values():
    ts = datetime.datetime(2025, 1, 1)
    m = Message(text="err", sender="Srv", msg_type="error", timestamp=ts)
    assert m.text == "err"
    assert m.sender == "Srv"
    assert m.msg_type == "error"
    assert m.timestamp == ts
    print("  OK custom values")


def test_timestamp_is_datetime():
    m = Message(text="x")
    assert isinstance(m.timestamp, datetime.datetime)
    print("  OK timestamp is datetime")


def test_dataclass_equality():
    ts = datetime.datetime(2025, 1, 1)
    a = Message(text="a", sender="s", msg_type="info", timestamp=ts)
    b = Message(text="a", sender="s", msg_type="info", timestamp=ts)
    assert a == b
    print("  OK dataclass equality")


if __name__ == "__main__":
    test_default_values()
    test_custom_values()
    test_timestamp_is_datetime()
    test_dataclass_equality()
    print("\nAll MessageModel tests passed.")
