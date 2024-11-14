"""Tests for the data models use in Node Mailer."""

from node_mailer.data_models import NodeMailerClient, NodeMailerMail


def test_node_mailer_client():
    """Tests the NodeMailerClient dataclass."""
    client = NodeMailerClient("Test name", "test ip", False)
    assert client.name == "Test name"
    assert client.ip_address == "test ip"
    assert client.favorite == False


def test_node_mailer_mail():
    """Tests the NodeMailerMail dataclass."""
    mail = NodeMailerMail("Test sender", "Test message", "Test node string", 123)
    assert mail.sender_name == "Test sender"
    assert mail.message == "Test message"
    assert mail.node_string == "Test node string"
    assert mail.timestamp == 123
    assert (
        mail.as_json()
        == '{"sender_name": "Test sender", "message": "Test message", "node_string": "Test node string", "timestamp": 123}'
    )
