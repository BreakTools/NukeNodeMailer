"""Functions for messaging between Node Mailer instances on the local network.

Written by Mervin van Brakel, 2024."""

import json

from PySide2 import QtCore, QtNetwork

from node_mailer import constants
from node_mailer.models.data_models import NodeMailerClient, NodeMailerMessage


class DirectMessagingHandler(QtCore.QObject):
    """Class that handles everything related to directly sending messages to other clients across the network.
    Uses TCP to receive/send data."""

    message_received = QtCore.Signal(NodeMailerMessage)

    def __init__(self):
        """Initializes the messaging handler."""
        super().__init__()
        self.tcp_server = QtNetwork.QTcpServer()
        self.tcp_server.newConnection.connect(self.on_new_connection)

    def start_listening(self) -> None:
        """Starts listening for incoming messages."""
        self.tcp_server.listen(
            address=QtNetwork.QHostAddress.AnyIPv4,
            port=constants.Ports.MESSAGING.value,
        )

    def on_new_connection(self) -> None:
        """Connects the readyRead signal to the on_message_received slot for new connections."""
        new_client = self.tcp_server.nextPendingConnection()
        new_client.readyRead.connect(
            lambda: self.on_message_received(new_client.readAll())
        )

    def on_message_received(self, message: QtCore.QByteArray) -> None:
        """Emits the processed message_received signal when a message is received.

        Args:
            message: The message that was received.
        """
        message_string = message.data().decode("utf-8")
        mailer_message = self.get_mailer_message_from_string(message_string)
        self.message_received.emit(mailer_message)

    def get_mailer_message_from_string(self, message_string: str) -> NodeMailerMessage:
        """Returns a NodeMailerMessage object from the network-sent string.

        Args:
            message_string: The JSON message in string form.

        Returns:
            The NodeMailerMessage object.
        """
        parsed_message = json.loads(message_string)
        return NodeMailerMessage(**parsed_message)

    def send_message(
        self, client: NodeMailerClient, message: NodeMailerMessage
    ) -> None:
        """Sends a message to another Node Mailer client.

        Args:
            client: The client to send the message to.
            message: The message to send.
        """
        tcp_socket = QtNetwork.QTcpSocket()
        tcp_socket.connectToHost(client.ip_address, constants.Ports.MESSAGING.value)

        tcp_socket.waitForConnected(2000)
        tcp_socket.write(message.as_json().encode("utf-8"))
        tcp_socket.waitForBytesWritten()
        tcp_socket.disconnectFromHost()
