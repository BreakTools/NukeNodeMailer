"""Tests for the history storage part of Node Mailer.

Written by Mervin van Brakel, 2024."""

import sqlite3
from unittest.mock import patch

from PySide2 import QtCore

from node_mailer.models.constants import MailHistoryRow
from node_mailer.models.data_models import NodeMailerMail
from node_mailer.models.history_storage import HistoryStorage


def test_get_database_path(tmp_path):
    """Tests the database path is correctly retrieved."""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()
        database_path = history_storage.get_database_path()

        assert database_path == tmp_path / "node_mailer" / "node_mailer_history.db"


def test_get_database_connection(tmp_path):
    """Tests the database connection is correctly retrieved.
    Situation where database doesn't yet exist is also covered because the get_database_connection
    function is called in the init function of the history storage class."""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()

        database = history_storage.get_database_connection()
        assert isinstance(database, sqlite3.Connection)


def test_create_database(tmp_path):
    """Test to see if the database is created properly if it doesn't exist."""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()

        database_path = tmp_path / "node_mailer" / "node_mailer_history.db"
        assert database_path.exists()

        database = history_storage.get_database_connection()
        cursor = database.cursor()
        cursor.execute("PRAGMA table_info(node_mailer_history)")
        columns = [column[1] for column in cursor.fetchall()]
        expected_columns = [
            "id",
            "sender_name",
            "description",
            "encoded_node_string",
            "timestamp",
        ]
        assert all(column in columns for column in expected_columns)


def test_retrieve_all_mail_from_database(tmp_path):
    """Tests the mail is retrieved from the database and stored in the TableModel"""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()
        add_fake_data_to_database(history_storage.database)
        history_storage.retrieve_all_mail_from_database()

        assert len(history_storage.mail_history) == 2
        assert history_storage.mail_history[0].sender_name == "Test sender2"
        assert history_storage.mail_history[1].sender_name == "Test sender"


def test_store_mail(tmp_path):
    """Tests the mail is inserted into database with the TableModel updating accordingly."""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()
        message = NodeMailerMail("Test sender", "Test message", "Test node string", 1)
        history_storage.store_mail(message)

        cursor = history_storage.database.cursor()
        cursor.execute("SELECT * FROM node_mailer_history")
        booking = cursor.fetchone()
        mail_id, sender_name, description, encoded_node_string, timestamp = booking

        assert mail_id == 1
        assert sender_name == "Test sender"
        assert description == "Test message"
        assert encoded_node_string == "Test node string"
        assert timestamp == 1

        assert len(history_storage.mail_history) == 1


def test_data(tmp_path):
    """Tests the data is correctly retrieved from the database for display in UI."""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()
        add_fake_data_to_database(history_storage.database)
        history_storage.retrieve_all_mail_from_database()

        assert (
            history_storage.data(history_storage.index(0, 0), QtCore.Qt.DisplayRole)
            == "Test sender2"
        )
        assert (
            history_storage.data(history_storage.index(0, 1), QtCore.Qt.DisplayRole)
            == "Test message2"
        )
        assert (
            history_storage.data(history_storage.index(0, 2), QtCore.Qt.DisplayRole)
            == 2
        )
        assert (
            history_storage.data(history_storage.index(1, 0), QtCore.Qt.DisplayRole)
            == "Test sender"
        )


def test_row_count(tmp_path):
    """Tests the row count is correctly retrieved from the database for display in UI."""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()
        assert history_storage.rowCount(None) == 0

        add_fake_data_to_database(history_storage.database)
        history_storage.retrieve_all_mail_from_database()
        assert history_storage.rowCount(None) == 2


def test_column_count(tmp_path):
    """Tests the column count is correctly retrieved from the database for display in UI."""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()
        assert history_storage.columnCount(None) == len(MailHistoryRow)


def test_get_mailer_data_from_index(tmp_path):
    """Tests a NodeMailerMessage object can be retrieved from a given index."""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()
        add_fake_data_to_database(history_storage.database)
        history_storage.retrieve_all_mail_from_database()

        message = history_storage.get_mailer_data_from_index(
            history_storage.index(1, 0)
        )
        assert message.sender_name == "Test sender"
        assert message.description == "Test message"
        assert message.node_string == "Test node string"
        assert message.timestamp == 1


def add_fake_data_to_database(database: sqlite3.Connection) -> None:
    """Helper function to configure database with fake data for tests."""
    cursor = database.cursor()
    cursor.execute(
        """INSERT INTO node_mailer_history (
            sender_name,
            description,
            encoded_node_string,
            timestamp
        ) VALUES ('Test sender', 'Test message', 'Test node string', 1)"""
    )
    cursor.execute(
        """INSERT INTO node_mailer_history (
            sender_name,
            description,
            encoded_node_string,
            timestamp
        ) VALUES ('Test sender2', 'Test message2', 'Test node string2', 2)"""
    )
    database.commit()
