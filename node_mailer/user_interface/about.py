"""User interface code for the About window.

Written by Mervin van Brakel, 2024."""

from pathlib import Path

from PySide2 import QtCore, QtGui, QtWidgets

from node_mailer.styled_widgets.window import NodeMailerWindow


class AboutWindow(NodeMailerWindow):
    """The About window for Node Mailer."""

    def __init__(self):
        """Initializes the About window."""
        super().__init__(
            self.get_user_interface(), "Node Mailer: About...", resizable=False
        )

    def get_user_interface(self):
        """Returns the user interface for the About window."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)
        widget.setLayout(layout)

        label_version = QtWidgets.QLabel("Node Mailer V[VERSION_NUMBER]")
        label_version.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label_version)

        label_developer = QtWidgets.QLabel("Developed with <3 by Mervin van Brakel")
        label_developer.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label_developer)

        github_label = QtWidgets.QLabel()
        github_label.setText(
            '<a href="https://github.com/BreakTools/NukeNodeMailer">Check out the source code on GitHub!</a>'
        )
        github_label.setOpenExternalLinks(True)
        github_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(github_label)

        layout.addWidget(self.get_gif_widget())

        return widget

    def get_gif_widget(self) -> QtWidgets.QWidget:
        """Returns a widget with a gif of me giving a thumbs up. Took me a whole morning to make
        so you better enjoy it!!"""
        path_to_gif = str(
            Path(__file__).parent.parent / "resources" / "thumbs_up_gif.gif"
        )
        gif_label = QtWidgets.QLabel()
        gif = QtGui.QMovie(path_to_gif)
        gif.setScaledSize(QtCore.QSize(300, 225))
        gif_label.setMovie(gif)
        gif.start()

        return gif_label
