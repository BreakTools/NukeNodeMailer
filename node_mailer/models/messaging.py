"""Functions for messaging between Node Mailer instances on the local network.

Written by Mervin van Brakel, 2024."""

import json
from typing import List

from PySide2 import QtCore, QtNetwork

from node_mailer.data_models import (
    NodeMailerClient,
    NodeMailerMail,
    ReceivingConnection,
)
from node_mailer.models import constants


class DirectMessaging(QtCore.QObject):
    """Model that handles everything related to directly sending messages to other clients across the network.
    Uses TCP to receive/send data."""

    message_received = QtCore.Signal(NodeMailerMail)

    def __init__(self) -> None:
        """Initializes the messaging handler."""
        super().__init__()
        self.tcp_server = QtNetwork.QTcpServer()
        self.tcp_server.newConnection.connect(self.on_new_connection)
        self.open_connections: List[ReceivingConnection] = []
        self.start_listening()

    def start_listening(self) -> None:
        """Starts listening for incoming messages."""
        self.tcp_server.listen(
            address=QtNetwork.QHostAddress.AnyIPv4,
            port=constants.Ports.MESSAGING.value,
        )

    def on_new_connection(self) -> None:
        """Connects the readyRead signal to the on_message_received slot for new connections."""
        new_client = self.tcp_server.nextPendingConnection()
        receiving_connection = ReceivingConnection(socket=new_client, message="")
        new_client.readyRead.connect(
            lambda: self.on_message_received(receiving_connection)
        )
        new_client.disconnected.connect(
            lambda: self.on_connection_closed(receiving_connection)
        )
        self.open_connections.append(receiving_connection)

    def on_message_received(self, connection: ReceivingConnection) -> None:
        """Emits the processed message_received signal when a message is received.

        Args:
            connection: The connection that is sending messages.
        """
        connection.message += connection.socket.readAll().data().decode("utf-8")

    def on_connection_closed(self, connection: ReceivingConnection) -> None:
        """Closed connection means we have received all the data. We can now process the message.

        Args:
            connection: The connection that was closed.
        """
        mail = self.get_mail_from_message_string(connection.message)
        self.message_received.emit(mail)
        self.open_connections.remove(connection)

    def get_mail_from_message_string(self, message_string: str) -> NodeMailerMail:
        """Returns a NodeMailerMessage object from the network-sent string.

        Args:
            message_string: The JSON message in string form.

        Returns:
            The NodeMailerMessage object.
        """
        parsed_message = json.loads(message_string)
        return NodeMailerMail(**parsed_message)

    def send_mail_to_client(
        self, mail: NodeMailerMail, client: NodeMailerClient
    ) -> None:
        """Sends a mail message to another Node Mailer client.

        Args:
            mail: The mail to send.
            client: The client to send the message to.
        """
        tcp_socket = QtNetwork.QTcpSocket()
        tcp_socket.connectToHost(client.ip_address, constants.Ports.MESSAGING.value)

        if not tcp_socket.waitForConnected(2000):
            msg = f"Could not connect to client {client.name}. Is it still running?"
            raise ConnectionError(msg)

        tcp_socket.write(mail.as_json().encode("utf-8"))
        tcp_socket.waitForBytesWritten()
        tcp_socket.disconnectFromHost()
