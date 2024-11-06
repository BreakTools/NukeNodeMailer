"""Code that handles the storage of mail history using sqlite3.

Written by Mervin van Brakel, 2024."""

from PySide2 import QtCore


class HistoryStorage(QtCore.QAbstractTableModel):
    """"""

    def __init__(self):
        super().__init__()
        self.database = None
        self.mail_history = []
        self.ensure_database_exists()

    def ensure_database_exists(self):
        pass

    def insert_mail_into_database(self):
        pass

    def retrieve_mail_from_database(self):
        pass

    def data(self, index, role):
        pass

    def rowCount(self):  # noqa: N802
        pass

    def columnCount(self):  # noqa: N802
        pass

    def get_mailer_data_from_index(self, index):
        pass
