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
    shutdown_received = QtCore.Signal()

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

    def stop_listening(self) -> None:
        """Stops listening for incoming messages."""
        self.tcp_server.close()

    def on_new_connection(self) -> None:
        """Connects the readyRead signal to the on_message_received slot for new connections."""
        new_client = self.tcp_server.nextPendingConnection()
        receiving_connection = ReceivingConnection(socket=new_client, message="")
        new_client.readyRead.connect(
            lambda: self.on_message_received(receiving_connection)
        )
        new_client.disconnected.connect(
            lambda: self.process_received_message(receiving_connection)
        )
        self.open_connections.append(receiving_connection)

    def on_message_received(self, connection: ReceivingConnection) -> None:
        """Emits the processed message_received signal when a message is received.

        Args:
            connection: The connection that is sending messages.
        """
        connection.message += connection.socket.readAll().data().decode("utf-8")

    def process_received_message(self, connection: ReceivingConnection) -> None:
        """Processes the complete received message we have stored when the sending connection closes.

        Args:
            connection: The connection that was closed.
        """
        try:
            parsed_message = json.loads(connection.message)
        except json.JSONDecodeError:
            return

        if parsed_message["type"] == "shutdown":
            self.shutdown_received.emit()
            return

        mail = NodeMailerMail(**parsed_message["mail"])
        self.message_received.emit(mail)
        self.open_connections.remove(connection)

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

        if not tcp_socket.waitForConnected(500):
            msg = f"Could not connect to client {client.name}. Is it still running?"
            raise ConnectionError(msg)

        dict_mail = {"type": "mail"}
        dict_mail["mail"] = mail.as_dict()

        tcp_socket.write(json.dumps(dict_mail).encode("utf-8"))
        tcp_socket.waitForBytesWritten()
        tcp_socket.disconnectFromHost()
        tcp_socket.close()

    def send_shutdown_message(self) -> None:
        """Sends a shutdown message to the local running Node Mailer instance."""
        tcp_socket = QtNetwork.QTcpSocket()
        tcp_socket.connectToHost("localhost", constants.Ports.MESSAGING.value)

        if not tcp_socket.waitForConnected(500):
            return

        shutdown_message = {"type": "shutdown"}
        tcp_socket.write(json.dumps(shutdown_message).encode("utf-8"))
        tcp_socket.waitForBytesWritten()
        tcp_socket.disconnectFromHost()
        tcp_socket.close()
