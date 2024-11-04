"""Tests for the code that handles direct messaging between two mailer instances."""

import json

import pytest
from PySide2 import QtCore, QtNetwork

from node_mailer import constants
from node_mailer.models.data_models import NodeMailerClient, NodeMailerMessage
from node_mailer.networking.messaging import DirectMessagingHandler


def test_on_message_received(qtbot):
    """Tests the message_received signal is properly emitted."""
    messaging_handler = DirectMessagingHandler()
    messaging_handler.start_listening()
    test_message = NodeMailerMessage(
        "test_user", "test_description", "test_node_string"
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


def test_get_mailer_message_from_string():
    """Tests we get a proper dataclass from the network-sent string."""
    messaging_handler = DirectMessagingHandler()

    message_string = "total gibberish"
    with pytest.raises(json.JSONDecodeError):
        messaging_handler.get_mailer_message_from_string(message_string)

    message_string = '{"sender_name": "test_user", "description": "test_description", "node_string": "test_node_string"}'

    assert messaging_handler.get_mailer_message_from_string(
        message_string
    ) == NodeMailerMessage("test_user", "test_description", "test_node_string")


def test_send_message(qtbot):
    """Tests the message is properly sent."""
    messaging_handler = DirectMessagingHandler()
    mailer_client = NodeMailerClient("test_user", "localhost")
    test_message = NodeMailerMessage(
        "test_user", "test_description", "test_node_string"
    )
    test_server = QtNetwork.QTcpServer()
    test_server.listen(port=constants.Ports.MESSAGING.value)

    with qtbot.waitSignal(test_server.newConnection, timeout=1000):
        messaging_handler.send_message(mailer_client, test_message)

    client = test_server.nextPendingConnection()
    with qtbot.waitSignal(client.readyRead, timeout=1000):
        pass

    message = client.readAll()
    assert message == QtCore.QByteArray(
        b'{"sender_name": "test_user", "description": "test_description", "node_string": "test_node_string"}'
    )
