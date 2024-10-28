"""Functions that handle auto discovery of other Node Mailer instances on the local network using UDP broadcasting.

Written by Mervin van Brakel, 2024."""

import json
import os

from PySide2 import QtCore, QtNetwork

from .. import constants


class MailingClientsFinder(QtCore.QObject):
    """"""

    def __init__(self):
        self.mailing_clients = []
        self.udp_socket = QtNetwork.QUdpSocket()
        self.udp_socket.bind(QtNetwork.QHostAddress.Broadcast)
        self.udp_socket.readyRead.connect(self.process_received_client_message)

        self.broadcast_message = self.get_broadcast_message()
        self.start_infinitely_broadcasting()

    def get_broadcast_message(self) -> str:
        """Returns the message that should be broadcasted to other Nuke instances."""
        login_name = os.getlogin()
        self.broadcast_message = json.dumps(
            {"type": "node_mailer_instance", "name": login_name}
        )

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

    def process_received_client_message(self) -> None:
        """Processes a received message from a client."""
        while self.udp_socket.hasPendingDatagrams():
            datagram = self.udp_socket.receiveDatagram()

            try:
                data = json.loads(datagram.data().data().decode("utf-8"))
            except json.JSONDecodeError:
                return

            if data.get("type") != "node_mailer_instance":
                return

            peer_address = datagram.senderAddress().toString()
            self.mailing_clients.append(peer_address)
