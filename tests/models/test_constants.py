"""Tests for model constants.

Written by Mervin van Brakel, 2024."""

from node_mailer.models.constants import MailHistoryRow


def test_mail_history_row():
    """Tests the mail history row enum."""
    assert len(MailHistoryRow) == 3

    assert MailHistoryRow.SENDER_NAME.column_index == 0
    assert MailHistoryRow.SENDER_NAME.display_name == "Sender Name"
    assert MailHistoryRow.SENDER_NAME.dataclass_field == "sender_name"
