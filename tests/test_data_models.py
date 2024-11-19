"""Tests for the data models use in Node Mailer."""

from node_mailer.data_models import NodeMailerMail


def test_node_mailer_mail():
    """Tests the NodeMailerMail dataclass."""
    mail = NodeMailerMail("Test sender", "Test message", "Test node string", 123)

    assert (
        mail.as_json()
        == '{"sender_name": "Test sender", "message": "Test message", "node_string": "Test node string", "timestamp": 123}'
    )
