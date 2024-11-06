"""Tests for the history storage part of Node Mailer.

Written by Mervin van Brakel, 2024."""

import sqlite3
from unittest.mock import patch

from PySide2 import QtCore

from node_mailer.models.data_models import NodeMailerMessage
from node_mailer.models.history_storage import HistoryStorage


def test_ensure_database_exists(tmp_path):
    """Test to see if the database is created if it doesn't exist."""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()
        history_storage.ensure_database_exists()

        database_path = tmp_path / "node_mailer" / "node_mailer_history.db"
        assert database_path.exists()

        database = sqlite3.connect(database_path)
        cursor = database.cursor()
        cursor.execute("PRAGMA table_info(node_mailer_history)")
        columns = [column[1] for column in cursor.fetchall()]
        expected_columns = [
            "id",
            "timestamp",
            "sender_name",
            "description",
            "encoded_node_string",
        ]
        assert all(column in columns for column in expected_columns)


def test_insert_mail_into_database(tmp_path):
    """Tests the mail is inserted into database with the TableModel updating accordingly."""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()
        message = NodeMailerMessage(
            "Test sender", "Test message", "Test node string", 1
        )
        history_storage.insert_mail_into_database(message)

        cursor = history_storage.database.cursor()
        cursor.execute("SELECT * FROM node_mailer_history")
        booking = cursor.fetchone()
        mail_id, timestamp, sender_name, description, encoded_node_string = booking

        assert mail_id == 1
        assert timestamp == 1
        assert sender_name == "Test sender"
        assert description == "Test message"
        assert encoded_node_string == "Test node string"

        assert history_storage.rowCount() == 1


def test_retrieve_mail_from_database(tmp_path):
    """Tests the mail is retrieved from the database and stored in the TableModel"""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()
        history_storage.retrieve_mail_from_database()
        add_fake_data_to_database(history_storage.database)

        assert history_storage.rowCount() == 1
        assert (
            history_storage.data(history_storage.index(0, 1), QtCore.Qt.DisplayRole)
            == "Test sender"
        )


def test_data(tmp_path):
    """Tests the data is correctly retrieved from the database for display in UI."""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()
        add_fake_data_to_database(history_storage.database)
        history_storage.retrieve_mail_from_database()

        assert (
            history_storage.data(history_storage.index(0, 0), QtCore.Qt.DisplayRole)
            == 1
        )
        assert (
            history_storage.data(history_storage.index(0, 1), QtCore.Qt.DisplayRole)
            == "Test sender"
        )
        assert (
            history_storage.data(history_storage.index(0, 2), QtCore.Qt.DisplayRole)
            == "Test message"
        )
        assert (
            history_storage.data(history_storage.index(0, 3), QtCore.Qt.DisplayRole)
            == "Test node string"
        )


def test_row_count(tmp_path):
    """Tests the row count is correctly retrieved from the database for display in UI."""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()
        assert history_storage.rowCount() == 0

        add_fake_data_to_database(history_storage.database)
        history_storage.retrieve_mail_from_database()
        assert history_storage.rowCount() == 1


def test_column_count(tmp_path):
    """Tests the column count is correctly retrieved from the database for display in UI."""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()
        assert history_storage.columnCount() == 4


def test_get_mailer_data_from_index(tmp_path):
    """Tests a NodeMailerMessage object can be retrieved from a given index."""
    with patch(
        "PySide2.QtCore.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        history_storage = HistoryStorage()
        add_fake_data_to_database(history_storage.database)
        history_storage.retrieve_mail_from_database()

        message = history_storage.get_mailer_data_from_index(
            history_storage.index(0, 0)
        )
        assert message.sender_name == "Test sender"
        assert message.description == "Test message"
        assert message.node_string == "Test node string"


def add_fake_data_to_database(database: sqlite3.Connection) -> None:
    """Helper function to configure database with fake data for tests."""
    cursor = database.cursor()

    cursor.execute(
        """CREATE TABLE node_mailer_history (
            id INTEGER PRIMARY KEY,
            timestamp INTEGER,
            sender_name TEXT,
            description TEXT,
            encoded_node_string TEXT
        )"""
    )
    cursor.execute(
        """INSERT INTO node_mailer_history (
            timestamp,
            sender_name,
            description,
            encoded_node_string
        ) VALUES (1, 'Test sender', 'Test message', 'Test node string')"""
    )
    database.commit()
