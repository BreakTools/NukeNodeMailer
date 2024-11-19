"""Tests for the code that handles auto discovery of other running Nuke instances on the network."""

from datetime import datetime
from unittest.mock import MagicMock, patch

from PySide2 import QtCore, QtGui, QtNetwork

from node_mailer.data_models import NodeMailerClient
from node_mailer.models import constants
from node_mailer.models.discovery import ClientDiscovery


def test_get_local_ip_addresses():
    """Test to make sure we only get proper local IPv4 addresses."""

    discovery = ClientDiscovery()
    with patch(
        "PySide2.QtNetwork.QNetworkInterface.allAddresses",
        return_value=[
            QtNetwork.QHostAddress("145.90.27.1"),
            QtNetwork.QHostAddress("127.0.0.1"),
            QtNetwork.QHostAddress("2001:0db8:85a3:0000:0000:8a2e:0370:7334"),
        ],
    ):
        local_ips = discovery.get_local_ip_addresses()
        assert "145.90.27.1" in local_ips
        assert "127.0.0.1" not in local_ips
        assert "2001:0db8:85a3:0000:0000:8a2e:0370:7334" not in local_ips


def test_get_broadcast_message():
    """Test the broadcast message."""
    discovery = ClientDiscovery()
    with patch("os.getlogin", return_value="test_user"):
        assert (
            discovery.get_broadcast_message()
            == '{"type": "node_mailer_instance", "name": "test_user"}'
        )


def test_broadcast_presence(qtbot):
    """Tests that the UDP broadcast data is properly sent."""
    discovery = ClientDiscovery()
    discovery.broadcast_message = (
        '{"type": "node_mailer_instance", "name": "test_user"}'
    )
    discovery.udp_socket.abort()

    test_listening_socket = QtNetwork.QUdpSocket()
    test_listening_socket.bind(
        QtNetwork.QHostAddress(QtNetwork.QHostAddress.AnyIPv4),
        constants.Ports.BROADCAST.value,
    )

    with qtbot.waitSignal(test_listening_socket.readyRead, timeout=10000) as blocker:
        discovery.start_background_processes()

    while test_listening_socket.hasPendingDatagrams():
        datagram = test_listening_socket.receiveDatagram()

    assert datagram.data().data().decode("utf-8") == discovery.broadcast_message


def test_remove_stale_clients(freezer):
    """Tests that stale clients are removed."""
    discovery = ClientDiscovery()
    discovery.mailing_clients = [
        NodeMailerClient(
            "test_name", "fake_ip", False, datetime.now().timestamp() - 31
        ),
        NodeMailerClient(
            "test_name2", "fake_ip2", False, datetime.now().timestamp() - 10
        ),
    ]

    discovery.remove_stale_clients()
    assert len(discovery.mailing_clients) == 1
    assert discovery.mailing_clients[0].name == "test_name2"


def test_process_datagram(freezer):
    """Tests the datagram is properly processed."""
    discovery = ClientDiscovery()
    mock_datagram = MagicMock()

    # Supposed to fail silently
    mock_datagram.data.return_value.data.return_value.decode.return_value = (
        "randomnonjsonstring"
    )
    discovery.process_datagram(mock_datagram)

    # Supposed to fail silently
    mock_datagram.data.return_value.data.return_value.decode.return_value = (
        '{"test": "test"}'
    )
    discovery.process_datagram(mock_datagram)

    mock_datagram.data.return_value.data.return_value.decode.return_value = (
        '{"name": "test_name"}'
    )
    mock_datagram.senderAddress.return_value.toString.return_value = "145.90.27.1"
    discovery.process_datagram(mock_datagram)

    assert len(discovery.mailing_clients) == 1
    assert discovery.mailing_clients[0].name == "test_name"
    assert discovery.mailing_clients[0].ip_address == "145.90.27.1"
    assert not discovery.mailing_clients[0].favorite
    assert (
        discovery.mailing_clients[0].last_seen_timestamp == datetime.now().timestamp()
    )


def test_sort_by_favorites():
    """Tests the sorting by favorites function."""
    discovery = ClientDiscovery()
    discovery.mailing_clients = [
        NodeMailerClient("test_name", "fake_ip", False, 0),
        NodeMailerClient("test_name2", "fake_ip2", True, 0),
    ]

    discovery.sort_by_favorites()
    assert discovery.mailing_clients[0].name == "test_name2"
    assert discovery.mailing_clients[1].name == "test_name"


def test_should_datagram_be_processed():
    """Test to check if the datagram should be processed."""
    discovery = ClientDiscovery()
    discovery.local_addresses = ["192.168.0.22"]
    discovery.mailing_clients = [
        NodeMailerClient("local_computer", "192.168.0.22", False, 0),
        NodeMailerClient("remote_computer", "192.168.0.23", False, 0),
    ]

    mock_datagram = MagicMock()
    mock_datagram.senderAddress.return_value.toString.return_value = "192.168.0.22"
    assert not discovery.should_datagram_be_processed(mock_datagram)

    mock_datagram.senderAddress.return_value.toString.return_value = "192.168.0.23"
    assert discovery.should_datagram_be_processed(mock_datagram)

    mock_datagram.senderAddress.return_value.toString.return_value = "192.168.0.24"
    assert discovery.should_datagram_be_processed(mock_datagram)


def test_get_stored_client_from_name():
    """Tests the get stored client function."""
    discovery = ClientDiscovery()
    discovery.mailing_clients = [
        NodeMailerClient("test_name", "fake_ip", False, 0),
    ]
    assert (
        discovery.get_stored_client_from_name("test_name")
        == discovery.mailing_clients[0]
    )
    assert discovery.get_stored_client_from_name("test_name2") is None


def test_update_client_last_seen_timestamp(freezer):
    """Tests the last seen timestamp is properly updated."""
    discovery = ClientDiscovery()
    discovery.mailing_clients = [
        NodeMailerClient("test_name", "fake_ip", False, 0),
    ]

    discovery.update_client_last_seen_timestamp(discovery.mailing_clients[0])

    assert (
        discovery.mailing_clients[0].last_seen_timestamp == datetime.now().timestamp()
    )


def test_data():
    """Tests the data function that is used for displaying text and icons in the UI.
    Wish I could tests if the QIcons are actually displaying the correct image but I'm running
    into a weird amount of crashes whenever I try to convert them and comparing them as images."""
    discovery = ClientDiscovery()
    discovery.mailing_clients = [
        NodeMailerClient("test_name", "fake_ip", False, 0),
        NodeMailerClient("test_name2", "fake_ip2", True, 0),
    ]
    assert discovery.data(discovery.index(0, 0), QtCore.Qt.DisplayRole) == "test_name"
    assert discovery.data(discovery.index(1, 0), QtCore.Qt.DisplayRole) == "test_name2"

    client_image_icon = discovery.data(discovery.index(0, 0), QtCore.Qt.DecorationRole)
    assert type(client_image_icon) == QtGui.QIcon
    favorite_client_image_icon = discovery.data(
        discovery.index(1, 0), QtCore.Qt.DecorationRole
    )
    assert type(favorite_client_image_icon) == QtGui.QIcon


def test_get_mailer_client_from_index():
    """Tests the client from index function."""
    discovery = ClientDiscovery()
    discovery.mailing_clients = [
        NodeMailerClient("test_name", "fake_ip", False, 0),
        NodeMailerClient("test_name2", "fake_ip2", True, 0),
    ]

    assert (
        discovery.get_mailer_client_from_index(discovery.index(0, 0)).name
        == "test_name"
    )
    assert (
        discovery.get_mailer_client_from_index(discovery.index(1, 0)).name
        == "test_name2"
    )


def test_row_count():
    """Tests the row count function that is used for display in the UI."""
    discovery = ClientDiscovery()
    discovery.mailing_clients = [NodeMailerClient("test_name", "fake_ip", False, 0)]
    assert discovery.rowCount(None) == 1


def test_toggle_favorite():
    """Tests the toggle favorite function."""
    with patch.object(
        ClientDiscovery, "add_favorite"
    ) as mock_add_favorite, patch.object(
        ClientDiscovery, "remove_favorite"
    ) as mock_remove_favorite:
        discovery = ClientDiscovery()
        discovery.mailing_clients = [
            NodeMailerClient("test_name", "fake_ip", False, 0),
            NodeMailerClient("test_name2", "fake_ip2", True, 0),
        ]

        discovery.toggle_favorite(discovery.index(0, 0))
        mock_add_favorite.assert_called_once_with("test_name")

        discovery.toggle_favorite(discovery.index(1, 0))
        mock_remove_favorite.assert_called_once_with("test_name2")


def test_is_favorite():
    """Tests is_favorite works properly."""
    with patch.object(QtCore.QSettings, "value", return_value="[]"):
        discovery = ClientDiscovery()
        assert not discovery.is_favorite("test_name")

    with patch.object(QtCore.QSettings, "value", return_value='["test_name"]'):
        discovery = ClientDiscovery()
        assert discovery.is_favorite("test_name")


def test_add_favorite():
    """Tests favorites are added properly."""
    with patch.object(QtCore.QSettings, "setValue") as mock_set_value:
        discovery = ClientDiscovery()
        discovery.add_favorite("test_name")
        mock_set_value.assert_called_once_with(
            constants.SettingStrings.FAVORITES.value, '["test_name"]'
        )


def test_remove_favorite():
    """Tests favorites are removed properly."""
    with patch.object(
        QtCore.QSettings, "value", return_value='["test_name", "test_name2"]'
    ), patch.object(QtCore.QSettings, "setValue") as mock_set_value:
        discovery = ClientDiscovery()
        discovery.remove_favorite("test_name")
        mock_set_value.assert_called_once_with(
            constants.SettingStrings.FAVORITES.value, '["test_name2"]'
        )
