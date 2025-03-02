"""User interface code for the various popups used in Node Mailer"""

from pathlib import Path

from PySide2 import QtCore, QtGui, QtWidgets

from node_mailer.audio_handler import play_error_sound
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
        super().__init__(
            self.get_user_interface(error_text), "Node Mailer: Error", resizable=False
        )
        play_error_sound()

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


def display_error_popup(error_text: str) -> None:
    """Displays an error popup with the given error text.

    Args:
        error_text: The error message to display.
    """
    error_popup = ErrorPopup(error_text)
    error_popup.exec_()


class YesNoPopup(NodeMailerWindow):
    """A popup window that displays a yes/no question."""

    closed = QtCore.Signal()

    def __init__(self, question_text: str) -> None:
        """Initializes the yes/no popup.

        Args:
            question_text: The question to display.
        """
        super().__init__(
            self.get_user_interface(question_text),
            "Node Mailer: Question",
            resizable=False,
        )
        self.picked_option = False

    def get_user_interface(self, question_text: str) -> QtWidgets.QWidget:
        """Returns the user interface for the yes/no popup.

        Args:
            question_text: The question to display.

        Returns:
            The widget with the yes/no popup user interface.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        layout.addWidget(self.get_question_widget(question_text))
        layout.addWidget(self.get_bottom_buttons())

        return widget

    def get_question_widget(self, question_text: str) -> QtWidgets.QWidget:
        """Returns the question widget for the yes/no popup.

        Args:
            question_text: The question to display.

        Returns:
            The widget with the question.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setSpacing(20)
        widget.setLayout(layout)

        question_icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(
            str(Path(__file__).parent.parent / "resources" / "question.png")
        )
        scaled_pixmap = pixmap.scaled(48, 48, QtCore.Qt.KeepAspectRatio)
        question_icon.setPixmap(scaled_pixmap)
        layout.addWidget(question_icon)

        question_text = QtWidgets.QLabel(question_text)
        question_text.setWordWrap(True)
        question_text.setMinimumWidth(250)
        layout.addWidget(question_text)

        return widget

    def get_bottom_buttons(self) -> QtWidgets.QWidget:
        """Returns the bottom buttons for the yes/no popup.

        Returns:
            The widget with the bottom buttons.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignRight)
        widget.setLayout(layout)

        no_button = NodeMailerButton("No")
        no_button.clicked.connect(self.on_no_clicked)
        layout.addWidget(no_button)

        yes_button = NodeMailerButton("Yes")
        yes_button.clicked.connect(self.on_yes_clicked)
        layout.addWidget(yes_button)

        return widget

    def on_no_clicked(self) -> None:
        """Handles the no button being clicked."""
        self.picked_option = False
        self.close()

    def on_yes_clicked(self) -> None:
        """Handles the yes button being clicked."""
        self.picked_option = True
        self.close()

    def exec_(self):
        """Executes the yes/no popup. Mimics the behavior of a blocking dialog."""
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


def display_yes_no_popup(question_text: str) -> bool:
    """Displays a yes/no popup with the given question text.

    Args:
        question_text: The question to display.

    Returns:
        True if the user clicked yes, False if the user clicked no.
    """
    yes_no_popup = YesNoPopup(question_text)
    yes_no_popup.exec_()
    return yes_no_popup.picked_option


class ReceivedMailPopup(NodeMailerWindow):
    """A popup window that display the received mail prompt."""

    closed = QtCore.Signal()

    def __init__(self, mail: NodeMailerMail) -> None:
        """Initializes the received mail popup.

        Args:
            mail: The received mail.
        """
        super().__init__(
            self.get_user_interface(mail),
            "Node Mailer: You've got mail!",
            resizable=False,
        )
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
            "Would you like to save the sent nodes for later or import them into your comp now?"
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
