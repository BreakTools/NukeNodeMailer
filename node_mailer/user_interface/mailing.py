"""User interface code for the Mailing window.

Written by Mervin van Brakel, 2024."""

from PySide2 import QtWidgets

from node_mailer.styled_widgets.window import NodeMailerWindow


class MailingWindow(NodeMailerWindow):
    """The Mailing window for Node Mailer."""

    def __init__(self):
        """Initializes the Mailing window."""
        super().__init__(self.get_user_interface(), "Node Mailer: Mail selected nodes")

    def get_user_interface(self):
        """Returns the user interface for the Mailing window."""
        return QtWidgets.QLabel("This is the Mailing window.")
