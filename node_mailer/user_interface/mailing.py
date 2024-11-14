"""User interface code for the Mailing window.

Written by Mervin van Brakel, 2024."""

from PySide2 import QtCore, QtWidgets

from node_mailer.data_models import NodeMailerClient
from node_mailer.models.discovery import ClientDiscovery
from node_mailer.styled_widgets.button import NodeMailerButton
from node_mailer.styled_widgets.utility import NoShadowStyle
from node_mailer.styled_widgets.window import NodeMailerWindow
from node_mailer.user_interface.popups import ErrorPopup


class MailingWindow(NodeMailerWindow):
    """The Mailing window for Node Mailer."""

    send_mail = QtCore.Signal(NodeMailerClient, str)

    def __init__(self, discovery_model: ClientDiscovery) -> None:
        """Initializes the Mailing window.

        Args:
            discovery_model: The model containing the available client data.
        """
        super().__init__(
            self.get_user_interface(discovery_model),
            "Node Mailer: Mail selected nodes",
        )

    def get_user_interface(self, discovery_model: ClientDiscovery) -> QtWidgets.QWidget:
        """Returns the user interface for the Mailing window.

        Args:
            discovery_model: The model containing the available client data.

        Returns:
            The widget with the mailing user interface.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        layout.addWidget(self.get_client_list_widget(discovery_model), 2)
        layout.addWidget(self.get_message_widget(), 1)
        layout.addWidget(self.get_bottom_buttons_widget())

        return widget

    def get_client_list_widget(self, discovery_model: ClientDiscovery):
        """Creates the connected list view for the client list.

        Args:
            discovery_model: The model containing the available client data.

        Returns:
            The connected list view.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        self.list_view = QtWidgets.QListView()
        self.list_view.setModel(discovery_model)
        self.list_view.setIconSize(QtCore.QSize(64, 64))
        self.list_view.setViewMode(QtWidgets.QListView.IconMode)
        self.list_view.setStyleSheet("""
            QListView {
            background-color: white;
            selection-background-color: white;
            }
            QListView::item:selected {
            background-color: #000BAB;
            selection-background-color: white;
            color: white;
            }
            QListView::item {
            color: black;
            }
        """)
        self.list_view.doubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_view)

        explainer_text = QtWidgets.QLabel(
            "Pro tip: Double click on a computer to add it to your favorites!"
        )
        explainer_text.setStyleSheet("font-size: 12px; color: #6E6E6E;")
        explainer_text.setStyle(NoShadowStyle())
        layout.addWidget(explainer_text)

        return widget

    def get_message_widget(self) -> QtWidgets.QWidget:
        """Returns the widget where the user can fill in the mail message.

        Returns:
            The message widget.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        message_label = QtWidgets.QLabel("Message:")
        message_label.setStyleSheet("font-size: 18px;")
        message_label.setStyle(NoShadowStyle())
        layout.addWidget(message_label)

        self.message_text_edit = QtWidgets.QTextEdit()
        self.message_text_edit.setStyleSheet("background-color: white;")
        layout.addWidget(self.message_text_edit)

        return widget

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

        cancel_button = NodeMailerButton("Cancel")
        cancel_button.clicked.connect(self.close)
        layout.addWidget(cancel_button)

        send_button = NodeMailerButton("Send")
        send_button.clicked.connect(self.on_send_mail_pressed)
        layout.addWidget(send_button)

        return widget

    def on_item_double_clicked(self, index: QtCore.QModelIndex) -> None:
        """Handles the double click event to mark a client as a favorite.

        Args:
            index: The index of the item that was double clicked.
        """
        self.list_view.model().toggle_favorite(index)

    def on_send_mail_pressed(self) -> None:
        """Emits the signal for sending the mail to the selected client."""
        selected_client_indexes = self.list_view.selectionModel().selectedIndexes()

        if not selected_client_indexes:
            error_popup = ErrorPopup(
                "You haven't selected a client to send the mail to!"
            )
            error_popup.exec_()
            return

        client = self.list_view.model().get_mailer_client_from_index(
            selected_client_indexes[0]
        )

        message = self.message_text_edit.toPlainText()

        self.send_mail.emit(client, message)
