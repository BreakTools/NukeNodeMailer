"""User interface code for the History window.

Written by Mervin van Brakel, 2024."""

from PySide2 import QtCore, QtWidgets

from node_mailer.data_models import NodeMailerMail
from node_mailer.models.history_storage import HistoryStorage
from node_mailer.styled_widgets.button import NodeMailerButton
from node_mailer.styled_widgets.utility import (
    NoShadowStyle,
    set_correct_highlight_color,
)
from node_mailer.styled_widgets.window import NodeMailerWindow
from node_mailer.user_interface.popups import display_error_popup


class HistoryWindow(NodeMailerWindow):
    """The History window for Node Mailer."""

    import_mail = QtCore.Signal(NodeMailerMail)

    def __init__(self, history_storage_model: HistoryStorage) -> None:
        """Initializes the History window.

        Args:
            history_storage_model: The model containing the history data.
        """
        super().__init__(
            self.get_user_interface(history_storage_model), "Node Mailer: Mail history"
        )

    def get_user_interface(
        self, history_storage_model: HistoryStorage
    ) -> QtWidgets.QWidget:
        """Returns the user interface for the History window.

        Args:
            history_storage_model: The model containing the history data.

        Returns:
            The widget with the history user interface.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)
        layout.addWidget(self.get_history_table(history_storage_model))
        layout.addWidget(self.get_bottom_buttons_widget())
        widget.setMinimumWidth(600)
        widget.setContentsMargins(0, 0, 0, 0)

        return widget

    def get_history_table(
        self, history_storage_model: HistoryStorage
    ) -> QtWidgets.QTableView:
        """Creates the connected table view for the history window.

        Args:
            history_storage_model: The model containing the history data.

        Returns:
            The connected table view.
        """
        self.table_view = QtWidgets.QTableView()
        self.table_view.setModel(history_storage_model)
        self.table_view.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch
        )
        self.table_view.setColumnWidth(2, 140)
        self.table_view.setStyleSheet("background-color: white;")
        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_view.horizontalHeader().setStyleSheet("background-color: #C6C6C6;")
        self.table_view.horizontalHeader().setStyle(NoShadowStyle())
        self.table_view.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)
        self.table_view.setStyle(NoShadowStyle())
        self.table_view.verticalScrollBar().setStyleSheet("background-color: #AFAFAF;")
        set_correct_highlight_color(self.table_view, "#AFAFAF")

        return self.table_view

    def get_bottom_buttons_widget(self) -> QtWidgets.QWidget:
        """Returns the bottom buttons widget for the History window.

        Returns:
            The bottom buttons widget.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignRight)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        delete_button = NodeMailerButton("Delete")
        delete_button.clicked.connect(self.delete_selected_mail)
        layout.addWidget(delete_button)

        import_button = NodeMailerButton("Import")
        import_button.clicked.connect(self.import_selected_mail)
        layout.addWidget(import_button)

        return widget

    def import_selected_mail(self) -> None:
        """Imports the selected mail from the history table."""
        selected_index = self.get_selected_index()
        if not selected_index:
            display_error_popup("No mail selected to import!")
            return

        selected_mail = self.table_view.model().get_mailer_data_from_index(
            selected_index
        )
        self.import_mail.emit(selected_mail)

    def delete_selected_mail(self) -> None:
        """Deletes the selected mail from the history storage model."""
        selected_index = self.get_selected_index()
        if not selected_index:
            display_error_popup("No mail selected to delete!")
            return

        self.table_view.model().delete_mail(selected_index)

    def get_selected_index(self) -> QtCore.QModelIndex:
        """Returns the selected index from the history table.

        Returns:
            The selected index.
        """
        selected_indexes = self.table_view.selectionModel().selectedRows()

        if not selected_indexes:
            return None

        return selected_indexes[0]
