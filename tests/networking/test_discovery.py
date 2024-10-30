"""Tests for the code that handles auto discovery of other running Nuke instances on the network.
For now I skip the actual testing of sent UDP packets here because I haven't figured out how to do that yet."""

from unittest.mock import MagicMock, patch

from PySide2 import QtNetwork

from node_mailer.models.data_models import NodeMailerClient
from node_mailer.networking.discovery import MailingClientsDiscovery


def test_get_local_ip_addresses():
    """Test to make sure we only get proper local IPv4 addresses."""
    discovery = MailingClientsDiscovery(start_broadcasting=False)
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
    discovery = MailingClientsDiscovery(start_broadcasting=False)
    with patch("os.getlogin", return_value="test_user"):
        assert (
            discovery.get_broadcast_message()
            == '{"type": "node_mailer_instance", "name": "test_user"}'
        )


def test_process_datagram():
    """Tests the datagram is properly processed."""
    discovery = MailingClientsDiscovery(start_broadcasting=False)
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


def test_should_datagram_be_processed():
    """Test to check if the datagram should be processed."""
    discovery = MailingClientsDiscovery(start_broadcasting=False)
    discovery.local_addresses = ["192.168.0.22"]
    discovery.mailing_clients = [
        NodeMailerClient("local_computer", "192.168.0.22"),
        NodeMailerClient("remote_computer", "192.168.0.23"),
    ]

    mock_datagram = MagicMock()
    mock_datagram.senderAddress.return_value.toString.return_value = "192.168.0.22"
    assert not discovery.should_datagram_be_processed(mock_datagram)

    mock_datagram.senderAddress.return_value.toString.return_value = "192.168.0.23"
    assert not discovery.should_datagram_be_processed(mock_datagram)

    mock_datagram.senderAddress.return_value.toString.return_value = "192.168.0.24"
    assert discovery.should_datagram_be_processed(mock_datagram)
