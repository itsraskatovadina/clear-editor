#! /usr/bin/env python3

import sys
import traceback

from PyQt5.QtWidgets import QApplication

from core.services.message_srv import MessageSrv, ErrorHandler


app = QApplication(sys.argv)


def _events():
    app.processEvents()


def test_info_routes_to_display_message():
    srv = MessageSrv()
    received = []

    def slot(html):
        received.append(html)

    srv.display_message.connect(slot)
    srv.post_message("hello", sender="Test", msg_type="info")
    _events()
    assert len(received) == 1
    assert "hello" in received[0]
    assert "[Test]" in received[0]
    print("  OK info → display_message")


def test_post_error_routes_to_display_error():
    srv = MessageSrv()
    received = []

    def slot(html):
        received.append(html)

    srv.display_error.connect(slot)
    srv.post_error("fail", "System")
    _events()
    assert len(received) == 1
    assert "fail" in received[0]
    print("  OK post_error → display_error")


def test_message_received_emitted():
    srv = MessageSrv()
    received = []

    def slot():
        received.append(True)

    srv.message_received.connect(slot)
    srv.post_message("test")
    _events()
    assert len(received) == 1
    print("  OK message_received emitted")


def test_post_message_error_routes_to_display_message():
    srv = MessageSrv()
    received = []

    srv.display_message.connect(lambda h: received.append(h))

    srv.post_message("error test", msg_type="error")
    _events()
    assert len(received) == 1
    print("  OK post_message error → display_message")


def test_display_error_not_called_on_info():
    srv = MessageSrv()
    msg_received = []
    err_received = []

    srv.display_message.connect(lambda h: msg_received.append(h))
    srv.display_error.connect(lambda h: err_received.append(h))

    srv.post_message("info test", msg_type="info")
    _events()
    assert len(msg_received) == 1
    assert len(err_received) == 0
    print("  OK info does not trigger display_error")


def test_warning_routes_to_display_message():
    srv = MessageSrv()
    received = []

    srv.display_message.connect(lambda h: received.append(h))
    srv.post_message("warn", msg_type="warning")
    _events()
    assert len(received) == 1
    print("  OK warning → display_message")


def test_debug_routes_to_display_message():
    srv = MessageSrv()
    received = []

    srv.display_message.connect(lambda h: received.append(h))
    srv.post_message("dbg", msg_type="debug")
    _events()
    assert len(received) == 1
    print("  OK debug → display_message")


def test_error_handler_with_message_srv_chain():
    srv = MessageSrv()
    received = []

    srv.display_error.connect(lambda h: received.append(h))
    srv.display_message.connect(lambda h: received.append(h))

    eh = ErrorHandler(srv.post_message)
    eh.write("error text")
    _events()
    assert len(received) == 1
    assert "error text" in received[0]
    print("  OK ErrorHandler → MessageSrv → display_error")


def test_error_handler_with_message_srv_chain_info():
    srv = MessageSrv()
    received = []

    srv.display_message.connect(lambda h: received.append(h))

    eh = ErrorHandler(lambda msg: srv.post_message(msg, "System", "info"))
    eh.write("info text")
    _events()
    assert len(received) == 1
    assert "info text" in received[0]
    print("  OK ErrorHandler → MessageSrv → display_message")


def test_excepthook_routes_via_error_handler():
    srv = MessageSrv()
    err_received = []

    srv.display_error.connect(lambda h: err_received.append(h))

    def on_error(msg):
        srv.post_error(msg, "System")

    eh = ErrorHandler(on_error)
    sys.excepthook = lambda exc_type, exc_value, exc_tb: eh.write(
        "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    )

    try:
        raise RuntimeError("test crash")
    except RuntimeError:
        exc_type, exc_value, exc_tb = sys.exc_info()
        sys.excepthook(exc_type, exc_value, exc_tb)

    _events()
    assert len(err_received) == 1
    assert "test crash" in err_received[0]
    print("  OK excepthook → ErrorHandler → MessageSrv → display_error")


def test_error_handler_forwards_to_handle():
    received = []

    def handle(msg):
        received.append(msg)

    eh = ErrorHandler(handle)
    eh.write("test stderr")
    assert len(received) == 1
    assert received[0] == "test stderr"
    print("  OK ErrorHandler.write forwards")


if __name__ == "__main__":
    test_info_routes_to_display_message()
    test_post_error_routes_to_display_error()
    test_message_received_emitted()
    test_post_message_error_routes_to_display_message()
    test_display_error_not_called_on_info()
    test_warning_routes_to_display_message()
    test_debug_routes_to_display_message()
    test_error_handler_with_message_srv_chain()
    test_error_handler_with_message_srv_chain_info()
    test_excepthook_routes_via_error_handler()
    test_error_handler_forwards_to_handle()
    print("\nAll MessageSrv tests passed.")
