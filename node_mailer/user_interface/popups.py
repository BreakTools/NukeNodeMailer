"""User interface code for the various popups used in Node Mailer"""

from pathlib import Path

from PySide2 import QtCore, QtGui, QtWidgets

from node_mailer.data_models import NodeMailerMail
from node_mailer.models.constants import ReceivedMailPopupOption
from node_mailer.styled_widgets.button import NodeMailerButton
from node_mailer.styled_widgets.utility import (
    NoShadowStyle,
    set_correct_highlight_color,
)
from node_mailer.styled_widgets.window import NodeMailerWindow


class ErrorPopup(NodeMailerWindow):
    """A popup window that displays an error message."""

    closed = QtCore.Signal()

    def __init__(self, error_text: str) -> None:
        """Initializes the error popup.

        Args:
            warning_text: The error message to display.
        """
        super().__init__(self.get_user_interface(error_text), "Node Mailer: Error")

    def get_user_interface(self, error_text: str) -> QtWidgets.QWidget:
        """Returns the user interface for the error popup.

        Args:
            message: The error message to display.

        Returns:
            The widget with the error popup user interface.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        layout.addWidget(self.get_error_widget(error_text))
        layout.addWidget(self.get_bottom_buttons())

        return widget

    def get_error_widget(self, error_text: str) -> QtWidgets.QWidget:
        """Returns the error widget for the error popup.

        Args:
            error_text: The error message to display.

        Returns:
            The widget with the error message.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setSpacing(20)
        widget.setLayout(layout)

        warning_icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(
            str(Path(__file__).parent.parent / "resources" / "warning.png")
        )
        scaled_pixmap = pixmap.scaled(48, 48, QtCore.Qt.KeepAspectRatio)
        warning_icon.setPixmap(scaled_pixmap)
        layout.addWidget(warning_icon)

        warning_text = QtWidgets.QLabel(error_text)
        warning_text.setWordWrap(True)
        warning_text.setMinimumWidth(250)
        layout.addWidget(warning_text)

        return widget

    def get_bottom_buttons(self) -> QtWidgets.QWidget:
        """Returns the bottom buttons for the error popup.

        Returns:
            The widget with the bottom buttons.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignRight)
        widget.setLayout(layout)

        ok_button = NodeMailerButton("OK")
        ok_button.clicked.connect(self.close)
        layout.addWidget(ok_button)

        return widget

    def exec_(self):
        """Executes the error popup. Mimics the behavior of a blocking dialog."""
        self.show()
        self.raise_()
        self.activateWindow()

        loop = QtCore.QEventLoop()
        self.closed.connect(loop.quit)
        loop.exec_()

    def closeEvent(self, event):  # noqa: N802
        """Emits the closed signal when the window is closed."""
        self.closed.emit()
        super().closeEvent(event)


class ReceivedMailPopup(NodeMailerWindow):
    """A popup window that display the received mail prompt."""

    closed = QtCore.Signal()

    def __init__(self, mail: NodeMailerMail) -> None:
        """Initializes the received mail popup.

        Args:
            mail: The received mail.
        """
        super().__init__(self.get_user_interface(mail), "Node Mailer: You've got mail!")
        self.picked_option = ReceivedMailPopupOption.IGNORE

    def get_user_interface(self, mail: NodeMailerMail) -> QtWidgets.QWidget:
        """Returns the user interface for the received message popup.

        Args:
            mail: The received mail.

        Returns:
            The widget with the received message popup user interface.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        layout.addWidget(self.get_mail_dialog_widget(mail))
        layout.addWidget(self.get_bottom_buttons())

        return widget

    def get_mail_dialog_widget(self, mail: NodeMailerMail) -> QtWidgets.QWidget:
        """Returns the message widget for the received message popup.

        Args:
            mail: The received mail.

        Returns:
            The widget that displays the mail dialog.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setSpacing(20)
        widget.setLayout(layout)

        mail_icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(
            str(Path(__file__).parent.parent / "resources" / "received_message.png")
        )
        scaled_pixmap = pixmap.scaled(48, 48, QtCore.Qt.KeepAspectRatio)
        mail_icon.setPixmap(scaled_pixmap)
        mail_icon.setAlignment(QtCore.Qt.AlignTop)
        mail_icon.setContentsMargins(0, 20, 0, 0)
        layout.addWidget(mail_icon)

        layout.addWidget(self.get_mail_contents_widget(mail))

        return widget

    def get_mail_contents_widget(self, mail: NodeMailerMail) -> QtWidgets.QWidget:
        """Returns the mail contents widget for the received message popup.

        Args:
            mail: The received mail.

        Returns:
            The widget that displays the mail contents.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        message_text = QtWidgets.QLabel(f"{mail.sender_name} has sent you mail!")
        layout.addWidget(message_text)

        message_display_textedit = QtWidgets.QTextEdit(mail.message)
        message_display_textedit.setReadOnly(True)
        message_display_textedit.setFixedSize(320, 100)
        message_display_textedit.setStyleSheet("background-color: white;")
        message_display_textedit.setStyle(NoShadowStyle())
        set_correct_highlight_color(message_display_textedit, "#000BAB")
        layout.addWidget(message_display_textedit)

        import_text = QtWidgets.QLabel(
            "Would you like to import the sent nodes now or save them in your history?"
        )
        import_text.setWordWrap(True)
        layout.addWidget(import_text)
        layout.addStretch()

        return widget

    def get_bottom_buttons(self) -> QtWidgets.QWidget:
        """Returns the bottom buttons for the received message popup.

        Returns:
            The widget with the bottom buttons.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignRight)
        widget.setLayout(layout)

        ignore_button = NodeMailerButton("Ignore")
        ignore_button.clicked.connect(self.close)
        layout.addWidget(ignore_button)

        save_button = NodeMailerButton("Save")
        save_button.clicked.connect(self.on_save_clicked)
        layout.addWidget(save_button)

        import_button = NodeMailerButton("Import")
        import_button.clicked.connect(self.on_import_clicked)
        layout.addWidget(import_button)

        return widget

    def on_save_clicked(self) -> None:
        """Handles the save button being clicked."""
        self.picked_option = ReceivedMailPopupOption.SAVE
        self.close()

    def on_import_clicked(self) -> None:
        """Handles the import button being clicked."""
        self.picked_option = ReceivedMailPopupOption.IMPORT
        self.close()

    def exec_(self):
        """Executes the received mail popup. Mimics the behavior of a blocking dialog."""
        self.show()
        self.raise_()
        self.activateWindow()

        loop = QtCore.QEventLoop()
        self.closed.connect(loop.quit)
        loop.exec_()

    def closeEvent(self, event):  # noqa: N802
        """Emits the closed signal when the window is closed."""
        self.closed.emit()
        super().closeEvent(event)
