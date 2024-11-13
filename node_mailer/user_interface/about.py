"""User interface code for the About window.

Written by Mervin van Brakel, 2024."""

from PySide2 import QtGui, QtWidgets

from node_mailer.styled_widgets.window import NodeMailerWindow


class AboutWindow(NodeMailerWindow):
    """The About window for Node Mailer."""

    def __init__(self):
        """Initializes the About window."""
        super().__init__(self.get_user_interface(), "Node Mailer: About...")

    def get_user_interface(self):
        """Returns the user interface for the About window."""
        return QtWidgets.QLabel("This is the About window.")
