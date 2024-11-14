"""Code that handles auto discovery of other Node Mailer instances on the local network using UDP broadcasting.

Written by Mervin van Brakel, 2024."""

import json
import os
from pathlib import Path
from typing import Any, List, Union

from PySide2 import QtCore, QtGui, QtNetwork

from node_mailer.data_models import NodeMailerClient
from node_mailer.models import constants


class ClientDiscovery(QtCore.QAbstractListModel):
    """Model that handles discovery and storage of other Node Mailer clients.
    Uses UDP broadcasting to find other instances on the local network."""

    def __init__(self) -> None:
        """Initializes the model class."""
        super().__init__()
        self.mailing_clients: List[NodeMailerClient] = []

        self.local_addresses = self.get_local_ip_addresses()
        self.broadcast_message = self.get_broadcast_message()

        self.store_icons()
        self.initialize_socket()
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
        """Initializes the socket and connects the signals."""
        self.udp_socket = QtNetwork.QUdpSocket()
        self.udp_socket.bind(
            QtNetwork.QHostAddress(QtNetwork.QHostAddress.AnyIPv4),
            constants.Ports.BROADCAST.value,
        )
        self.udp_socket.readyRead.connect(self.on_datagram_received)

    def store_icons(self) -> None:
        """Stores the icons this model should return."""
        self.mail_client_icon = self.get_correctly_displaying_icon(
            Path(__file__).parent.parent / "resources" / "mailer_client.png"
        )
        self.favorite_mail_client_icon = self.get_correctly_displaying_icon(
            Path(__file__).parent.parent / "resources" / "favorite_mailer_client.png"
        )

    def get_correctly_displaying_icon(self, path: Path) -> QtGui.QIcon:
        """Returns the QIcon that displays nicely in the UI.
        By default Qt will highlight selected list view icons, but that's not a thing in Window 95.
        As a workaround we need to set both the Normal and the Selected QIcon states to the same icon, because
        Qt only highlights the selected icon if there's no 'Selected' image stored on the QIcon it's displaying.

        Args:
            path: The path to the icon.

        Returns:
            The icon that will correctly display in the UI.
        """
        icon = QtGui.QIcon(str(path))
        icon.addFile(str(path), mode=QtGui.QIcon.Normal)
        icon.addFile(str(path), mode=QtGui.QIcon.Selected)
        return icon

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

            self.process_datagram(datagram)

    def process_datagram(self, datagram: QtNetwork.QNetworkDatagram) -> None:
        """Processes the datagram and adds the client to the mailing_clients list.

        Args:
            datagram: The datagram to process.
        """
        try:
            parsed_data = json.loads(datagram.data().data().decode("utf-8"))
        except json.JSONDecodeError:
            return

        try:
            mailer_client_name = parsed_data["name"]
        except KeyError:
            return

        self.mailing_clients.append(
            NodeMailerClient(
                mailer_client_name,
                datagram.senderAddress().toString(),
                self.is_favorite(mailer_client_name),
            )
        )
        self.sort_by_favorites()
        self.layoutChanged.emit()

    def sort_by_favorites(self) -> None:
        """Sorts our stored mailing clients so the favorites show up first."""
        self.mailing_clients.sort(key=lambda client: client.favorite, reverse=True)

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

    def data(self, index: QtCore.QModelIndex, role: Any) -> Union[str, QtGui.QIcon]:
        """Returns the text or icon for the given index and role.

        Args:
            index: The index of the item.
            role: The role the data plays in the UI.
        """
        if role == QtCore.Qt.DisplayRole:
            return self.mailing_clients[index.row()].name

        if role == QtCore.Qt.DecorationRole:
            if not self.mailing_clients[index.row()].favorite:
                return self.mail_client_icon

            return self.favorite_mail_client_icon

        return None

    def get_mailer_client_from_index(
        self, index: QtCore.QModelIndex
    ) -> NodeMailerClient:
        """Returns the mailer client from the given index.

        Args:
            index: The index of the mailer client.

        Returns:
            The mailer client at the given index.
        """
        return self.mailing_clients[index.row()]

    def rowCount(self, _) -> int:  # noqa: N802
        """Returns the number of mailing clients that have been found for use in UI.

        Returns:
            The number of mailing clients that have been found.
        """
        return len(self.mailing_clients)

    def toggle_favorite(self, index: QtCore.QModelIndex) -> None:
        """Toggles the favorite status of the client at the given index.

        Args:
            index: The index of the client to toggle the favorite status of.
        """
        client = self.mailing_clients[index.row()]
        if client.favorite:
            self.remove_favorite(client.name)
        else:
            self.add_favorite(client.name)

        client.favorite = not client.favorite
        self.sort_by_favorites()
        self.layoutChanged.emit()

    def is_favorite(self, client_name: str) -> bool:
        """Checks the QSettings to see if the client name is a favorite.

        Args:
            client: The client to check.

        Returns:
            True if the client is a favorite, False otherwise.
        """
        settings = QtCore.QSettings()
        favorites = settings.value(
            constants.SettingStrings.FAVORITES.value, defaultValue="[]"
        )
        parsed_favorites = json.loads(favorites)
        return client_name in parsed_favorites

    def add_favorite(self, client_name: str) -> None:
        """Adds the client to the favorites QSetting.

        Args:
            client: The client to add to the favorites.
        """
        settings = QtCore.QSettings()
        favorites = settings.value(
            constants.SettingStrings.FAVORITES.value, defaultValue="[]"
        )
        parsed_favorites = json.loads(favorites)
        parsed_favorites.append(client_name)
        settings.setValue(
            constants.SettingStrings.FAVORITES.value, json.dumps(parsed_favorites)
        )
        self.layoutChanged.emit()

    def remove_favorite(self, client_name: str) -> None:
        """Removes the client from the favorites QSetting

        Args:
            client: The client to remove from the favorites.
        """
        settings = QtCore.QSettings()
        favorites = settings.value(
            constants.SettingStrings.FAVORITES.value, defaultValue="[]"
        )
        parsed_favorites = json.loads(favorites)
        parsed_favorites.remove(client_name)
        settings.setValue(
            constants.SettingStrings.FAVORITES.value, json.dumps(parsed_favorites)
        )
