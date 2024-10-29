"""Code that handles auto discovery of other Node Mailer instances on the local network using UDP broadcasting.

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

        self.local_addresses = self.get_local_ip_addresses()
        self.initialize_socket()

        self.broadcast_message = self.get_broadcast_message()
        self.start_infinitely_broadcasting()

    def get_local_ip_addresses(self) -> List[str]:
        """Returns the local IP addresses of the machine. It's a list because some machines have
        multiple local IP addresses (like VPNs and stuff) and I don't know how to find the relevant one lol.

        Returns:
            The local IP addresses of the machine.
        """
        localhost = QtNetwork.QHostAddress(QtNetwork.QHostAddress.LocalHost)
        return [
            address.toString()
            for address in QtNetwork.QNetworkInterface.allAddresses()
            if address.protocol() == QtNetwork.QAbstractSocket.IPv4Protocol
            and address != localhost
        ]

    def initialize_socket(self) -> None:
        """Initializes the sockets and connects their signals."""
        self.udp_socket = QtNetwork.QUdpSocket()
        self.udp_socket.bind(
            QtNetwork.QHostAddress(QtNetwork.QHostAddress.AnyIPv4),
            constants.Ports.BROADCAST.value,
        )
        self.udp_socket.readyRead.connect(self.on_datagram_received)

    def get_broadcast_message(self) -> str:
        """Returns the message that should be broadcasted to other Nuke instances.

        Returns:
            The broadcast message.
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
        self.udp_socket.writeDatagram(
            QtCore.QByteArray(self.broadcast_message.encode("utf-8")),
            QtNetwork.QHostAddress.Broadcast,
            constants.Ports.BROADCAST.value,
        )

    def on_datagram_received(self) -> None:
        """Callback for when a datagram is received. Tries to parse the data and
        calls the process function for processing."""
        while self.udp_socket.hasPendingDatagrams():
            datagram = self.udp_socket.receiveDatagram()

            if not self.should_datagram_be_processed(datagram):
                continue

            parsed_data = json.loads(datagram.data().data().decode("utf-8"))

            self.mailing_clients.append(
                NodeMailerClient(
                    parsed_data["name"], datagram.senderAddress().toString()
                )
            )

    def should_datagram_be_processed(
        self, datagram: QtNetwork.QNetworkDatagram
    ) -> bool:
        """Checks if the datagram should be processed.

        Args:
            datagram: The datagram to check.
        """
        ip_address = datagram.senderAddress().toString()

        if ip_address in self.local_addresses:
            return False

        return all(client.ip_address != ip_address for client in self.mailing_clients)
