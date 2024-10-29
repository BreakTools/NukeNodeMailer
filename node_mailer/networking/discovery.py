"""Functions that handle auto discovery of other Node Mailer instances on the local network using UDP broadcasting.

Written by Mervin van Brakel, 2024."""

import json
import os
from typing import List

from PySide2 import QtCore, QtNetwork

from node_mailer import constants
from node_mailer.models.data_models import NodeMailerClient


class MailingClientsDiscovery(QtCore.QObject):
    """Class that handles discovery and storage of other Node Mailer clients.
    Uses UDP broadcasting to find other instances on the local network."""

    def __init__(self):
        """Initializes the MailingClientsDiscovery class."""
        self.mailing_clients: List[NodeMailerClient] = []

        self.initialize_sockets()

        self.broadcast_message = self.get_broadcast_message()
        self.start_infinitely_broadcasting()

    def initialize_sockets(self) -> None:
        """Initializes the sockets and connects their signals."""
        self.receiving_socket = QtNetwork.QUdpSocket()
        self.receiving_socket.bind(
            QtNetwork.QHostAddress(QtNetwork.QHostAddress.AnyIPv4),
            constants.Ports.BROADCAST.value,
        )

        self.receiving_socket.readyRead.connect(self.on_datagram_received)

        self.sending_socket = QtNetwork.QUdpSocket()

    def get_broadcast_message(self) -> str:
        """Returns the message that should be broadcasted to other Nuke instances.

        Returns:
            str: The broadcast message.
        """
        login_name = os.getlogin()
        return json.dumps({"type": "node_mailer_instance", "name": login_name})

    def start_infinitely_broadcasting(self) -> None:
        """Starts the loop that infinitely announces the Nuke instance on the local network
        so other Nuke instances can find it. Your Nuke is now a radio station!"""
        self.broadcast_timer = QtCore.QTimer()
        self.broadcast_timer.timeout.connect(self.broadcast_presence)
        self.broadcast_timer.start(2000)

    def broadcast_presence(self) -> None:
        """Broadcasts the presence of the Nuke instance on the local network."""
        self.sending_socket.writeDatagram(
            QtCore.QByteArray(self.broadcast_message.encode("utf-8")),
            QtNetwork.QHostAddress.Broadcast,
            constants.Ports.BROADCAST.value,
        )

    def on_datagram_received(self) -> None:
        """Callback for when a datagram is received. Tries to parse the data and
        calls the process function for processing."""
        while self.receiving_socket.hasPendingDatagrams():
            datagram = self.receiving_socket.receiveDatagram()

            parsed_data = json.loads(datagram.data().data().decode("utf-8"))

            self.process_received_client_message(
                parsed_data, datagram.senderAddress().toString()
            )

    def process_received_client_message(self, message: dict, ip_address: str) -> None:
        """Processes a received message from a client and stores it.

        Args:
            message: The message that was received.
            ip_address: The IP address of the client that sent the message.
        """
        if message.get("type") != "node_mailer_instance":
            return

        if message.get("name") == os.getlogin():
            return

        for client in self.mailing_clients:
            if client.ip_address == ip_address:
                return

        self.mailing_clients.append(NodeMailerClient(message.get("name"), ip_address))
