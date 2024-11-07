"""Code that handles the storage of mail history using sqlite3.

Written by Mervin van Brakel, 2024."""

import sqlite3
from pathlib import Path
from typing import List

from PySide2 import QtCore

from node_mailer.models.constants import MailHistoryRow
from node_mailer.models.data_models import NodeMailerMail


class HistoryStorage(QtCore.QAbstractTableModel):
    """Class that handles storage of received mails using a sqlite3 database."""

    def __init__(self):
        """Initializes the history storage by setting up the database connection and retrieving stored mails."""
        super().__init__()
        self.mail_history: List[NodeMailerMail] = []
        self.database_path = self.get_database_path()
        self.database = self.get_database_connection()
        self.retrieve_all_mail_from_database()

    def get_database_path(self) -> Path:
        """Finds the Nuke Qt writable location and return the path to the database.

        Returns:
            Path to the database.
        """
        nuke_save_folder = Path(
            QtCore.QStandardPaths.writableLocation(
                QtCore.QStandardPaths.AppDataLocation
            )
        )
        return nuke_save_folder / "node_mailer" / "node_mailer_history.db"

    def get_database_connection(self) -> sqlite3.Connection:
        """Returns the database connection, runs the create function if the database doesn't already exist.

        Returns:
            The database connection.
        """
        if self.database_path.exists():
            return sqlite3.connect(self.database_path)

        self.create_database()
        return sqlite3.connect(self.database_path)

    def create_database(self):
        """Creates the database and configures it."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        # Will implicitly create the database file
        database = sqlite3.connect(self.database_path)

        cursor = database.cursor()
        cursor.execute(
            """CREATE TABLE node_mailer_history (
            id INTEGER PRIMARY KEY,
            sender_name TEXT,
            description TEXT,
            encoded_node_string TEXT,
            timestamp INTEGER
        )"""
        )

        database.commit()
        database.close()

    def retrieve_all_mail_from_database(self):
        """Retrieves all the mails from the database and stored them als NodeMailerMail objects on this model."""
        cursor = self.database.cursor()
        cursor.execute("SELECT * FROM node_mailer_history ORDER BY timestamp DESC")
        self.mail_history = [
            NodeMailerMail(
                sender_name=row[1],
                description=row[2],
                node_string=row[3],
                timestamp=row[4],
            )
            for row in cursor.fetchall()
        ]

    def store_mail(self, mail: NodeMailerMail):
        """Stores the mail in the database.

        Args:
            mail: The mail to store.
        """
        self.mail_history.append(mail)
        self.database.execute(
            """INSERT INTO node_mailer_history (sender_name, description, encoded_node_string, timestamp)
            VALUES (?, ?, ?, ?)""",
            (mail.sender_name, mail.description, mail.node_string, mail.timestamp),
        )
        self.database.commit()

    def data(self, index, role):
        """Returns the data for the given index and role for use in the UI."""
        if role != QtCore.Qt.DisplayRole:
            return None

        if index.column() == MailHistoryRow.SENDER_NAME.column_index:
            return getattr(
                self.mail_history[index.row()],
                MailHistoryRow.SENDER_NAME.dataclass_field,
            )

        if index.column() == MailHistoryRow.DESCRIPTION.column_index:
            return getattr(
                self.mail_history[index.row()],
                MailHistoryRow.DESCRIPTION.dataclass_field,
            )

        if index.column() == MailHistoryRow.TIMESTAMP.column_index:
            return getattr(
                self.mail_history[index.row()],
                MailHistoryRow.TIMESTAMP.dataclass_field,
            )

        return None

    def rowCount(self, _):  # noqa: N802
        """Returns the number of rows in the model for display in UI."""
        return len(self.mail_history)

    def columnCount(self, _):  # noqa: N802
        """Returns the number of columns in the model for display in UI."""
        return len(MailHistoryRow)

    def get_mailer_data_from_index(self, index: QtCore.QModelIndex) -> NodeMailerMail:
        """Gets the NodeMailerMail object from the given index.

        Args:
            index: The index to get the data from.

        Returns:
            The NodeMailerMail object.
        """
        return self.mail_history[index.row()]
