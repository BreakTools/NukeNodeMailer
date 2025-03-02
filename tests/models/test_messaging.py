"""Tests for the code that handles direct messaging between two mailer instances."""

import json

from PySide2 import QtCore, QtNetwork

from node_mailer.data_models import NodeMailerClient, NodeMailerMail
from node_mailer.models import constants
from node_mailer.models.messaging import DirectMessaging


def test_process_received_message(qtbot):
    """Tests the mail is received and processed correctly."""
    messaging_handler = DirectMessaging()
    test_mail = NodeMailerMail("test_user", "test_description", "test_node_string", 0)
    message_dict = {"type": "mail"}
    message_dict["mail"] = test_mail.as_dict()

    assert len(messaging_handler.open_connections) == 0

    with qtbot.waitSignal(messaging_handler.message_received, timeout=1000) as blocker:
        tcp_socket = QtNetwork.QTcpSocket()
        tcp_socket.connectToHost("localhost", constants.Ports.MESSAGING.value)
        tcp_socket.waitForConnected()
        tcp_socket.write(json.dumps(message_dict).encode("utf-8"))
        tcp_socket.waitForBytesWritten()
        tcp_socket.disconnectFromHost()

    assert blocker.args[0] == test_mail
    assert len(messaging_handler.open_connections) == 0
    messaging_handler.tcp_server.close()


def test_send_mail_to_client(qtbot):
    """Tests the message is properly sent."""
    messaging_handler = DirectMessaging()
    messaging_handler.tcp_server.close()
    mailer_client = NodeMailerClient("test_user", "localhost", False, 0)
    test_mail = NodeMailerMail("test_user", "test_message", "test_node_string", 0)

    test_server = QtNetwork.QTcpServer()
    test_server.listen(port=constants.Ports.MESSAGING.value)
    with qtbot.waitSignal(test_server.newConnection, timeout=1000):
        messaging_handler.send_mail_to_client(test_mail, mailer_client)

    client = test_server.nextPendingConnection()
    with qtbot.waitSignal(client.readyRead, timeout=1000):
        pass

    message = client.readAll()
    assert message == QtCore.QByteArray(
        b'{"type": "mail", "mail": {"sender_name": "test_user", "message": "test_message", "node_string": "test_node_string", "timestamp": 0}}'
    )


def test_send_shutdown_message(qtbot):
    """Tests the shutdown message is properly sent."""
    messaging_handler = DirectMessaging()
    messaging_handler.tcp_server.close()

    test_server = QtNetwork.QTcpServer()
    test_server.listen(port=constants.Ports.MESSAGING.value)
    with qtbot.waitSignal(test_server.newConnection, timeout=1000):
        messaging_handler.send_shutdown_message()

    client = test_server.nextPendingConnection()
    with qtbot.waitSignal(client.readyRead, timeout=1000):
        pass

    message = client.readAll()
    assert message == QtCore.QByteArray(b'{"type": "shutdown"}')
