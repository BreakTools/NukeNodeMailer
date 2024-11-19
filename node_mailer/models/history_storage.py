"""Code that handles the storage of mail history using sqlite3.

Written by Mervin van Brakel, 2024."""

import sqlite3
from pathlib import Path
from typing import Any, List, Union

from PySide2 import QtCore, QtGui

from node_mailer.data_models import NodeMailerMail
from node_mailer.models.constants import MailHistoryRow


class HistoryStorage(QtCore.QAbstractTableModel):
    """Model that handles storage of received mails using a sqlite3 database."""

    def __init__(self) -> None:
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

    def create_database(self) -> None:
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

    def retrieve_all_mail_from_database(self) -> None:
        """Retrieves all the mails from the database and stored them als NodeMailerMail objects on this model."""
        cursor = self.database.cursor()
        cursor.execute("SELECT * FROM node_mailer_history ORDER BY timestamp DESC")
        self.mail_history = [
            NodeMailerMail(
                sender_name=row[1],
                message=row[2],
                node_string=row[3],
                timestamp=row[4],
            )
            for row in cursor.fetchall()
        ]

    def store_mail(self, mail: NodeMailerMail) -> None:
        """Stores the mail in the database.

        Args:
            mail: The mail to store.
        """
        mail.message = self.get_plain_text_from_html_string(mail.message)
        self.mail_history.insert(0, mail)
        self.database.execute(
            """INSERT INTO node_mailer_history (sender_name, description, encoded_node_string, timestamp)
            VALUES (?, ?, ?, ?)""",
            (mail.sender_name, mail.message, mail.node_string, mail.timestamp),
        )
        self.database.commit()
        self.layoutChanged.emit()

    def get_plain_text_from_html_string(self, html_string: str) -> str:
        """Converts a Qt rich text HTML string to a plain unformatted single line string.

        Args:
            html_string: The HTML string to convert.

        Returns:
            The plain text string.
        """
        document = QtGui.QTextDocument()
        document.setHtml(html_string)
        return document.toPlainText().replace("\n", " ")

    def delete_mail(self, index: QtCore.QModelIndex) -> None:
        """Deletes the mail from the database and the model.

        Args:
            index: The index of the mail to delete.
        """
        mail = self.mail_history[index.row()]
        self.database.execute(
            "DELETE FROM node_mailer_history WHERE encoded_node_string = ? AND timestamp = ?",
            (mail.node_string, mail.timestamp),
        )
        self.database.commit()
        self.mail_history.pop(index.row())
        self.layoutChanged.emit()

    def data(self, index: QtCore.QModelIndex, role: Any) -> Union[str, None]:
        """Returns the data for the given index and role for use in the UI."""
        if role != QtCore.Qt.DisplayRole:
            return None

        if index.column() == MailHistoryRow.SENDER_NAME.column_index:
            return getattr(
                self.mail_history[index.row()],
                MailHistoryRow.SENDER_NAME.dataclass_field,
            )

        if index.column() == MailHistoryRow.MESSAGE.column_index:
            return getattr(
                self.mail_history[index.row()],
                MailHistoryRow.MESSAGE.dataclass_field,
            )

        if index.column() == MailHistoryRow.TIMESTAMP.column_index:
            timestamp = getattr(
                self.mail_history[index.row()],
                MailHistoryRow.TIMESTAMP.dataclass_field,
            )
            return QtCore.QDateTime.fromSecsSinceEpoch(timestamp).toString(
                "dd-MM-yyyy hh:mm:ss"
            )

        return None

    def headerData(
        self, section: int, orientation: QtCore.Qt.Orientation, role: int
    ) -> str:  # noqa: N802
        """Returns the header data for the given section, orientation, and role.

        Args:
            section: The section to get the header data for.
            orientation: The orientation of the header.
            role: The role of the header data.

        Returns:
            The header text to display in the UI.
        """
        if role != QtCore.Qt.DisplayRole:
            return None

        if orientation == QtCore.Qt.Horizontal:
            if section == MailHistoryRow.SENDER_NAME.column_index:
                return MailHistoryRow.SENDER_NAME.display_name
            if section == MailHistoryRow.MESSAGE.column_index:
                return MailHistoryRow.MESSAGE.display_name
            if section == MailHistoryRow.TIMESTAMP.column_index:
                return MailHistoryRow.TIMESTAMP.display_name

        return None

    def rowCount(self, _) -> int:  # noqa: N802
        """Returns the number of rows in the model for display in UI."""
        return len(self.mail_history)

    def columnCount(self, _) -> int:  # noqa: N802
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
