"""Tests for the code that handles direct messaging between two mailer instances."""

import json

import pytest
from PySide2 import QtCore, QtNetwork

from node_mailer.data_models import NodeMailerClient, NodeMailerMail
from node_mailer.models import constants
from node_mailer.models.messaging import DirectMessaging


def test_on_message_received(qtbot):
    """Tests the message_received signal is properly emitted."""
    messaging_handler = DirectMessaging()
    messaging_handler.start_listening()
    test_message = NodeMailerMail(
        "test_user", "test_description", "test_node_string", 0
    )

    with qtbot.waitSignal(messaging_handler.message_received, timeout=1000) as blocker:
        tcp_socket = QtNetwork.QTcpSocket()
        tcp_socket.connectToHost("localhost", constants.Ports.MESSAGING.value)
        tcp_socket.waitForConnected()

        tcp_socket.write(test_message.as_json().encode("utf-8"))
        tcp_socket.waitForBytesWritten()
        tcp_socket.disconnectFromHost()

    assert blocker.args[0] == test_message
    messaging_handler.tcp_server.close()


def test_get_mail_from_message_string():
    """Tests we get a proper dataclass from the network-sent string."""
    messaging_handler = DirectMessaging()

    message_string = "total gibberish"
    with pytest.raises(json.JSONDecodeError):
        messaging_handler.get_mail_from_message_string(message_string)

    message_string = '{"sender_name": "test_user", "message": "test_message", "node_string": "test_node_string", "timestamp": 0}'

    assert messaging_handler.get_mail_from_message_string(
        message_string
    ) == NodeMailerMail("test_user", "test_message", "test_node_string", 0)


def test_send_mail_to_client(qtbot):
    """Tests the message is properly sent."""
    messaging_handler = DirectMessaging()
    mailer_client = NodeMailerClient("test_user", "localhost", False)
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
        b'{"sender_name": "test_user", "message": "test_message", "node_string": "test_node_string", "timestamp": 0}'
    )
