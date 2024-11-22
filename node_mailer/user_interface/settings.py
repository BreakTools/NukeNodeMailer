"""User interface code for the settings window.

Written by Mervin van Brakel, 2024."""

import os

from PySide2 import QtCore, QtWidgets

from node_mailer.models.constants import SettingStrings
from node_mailer.styled_widgets.button import NodeMailerButton
from node_mailer.styled_widgets.utility import (
    NoShadowStyle,
    set_checkbox_styling,
    set_correct_highlight_color,
)
from node_mailer.styled_widgets.window import NodeMailerWindow


class SettingsWindow(NodeMailerWindow):
    """The settings window for Node Mailer."""

    def __init__(self):
        """Initializes the settings window."""
        self.settings = QtCore.QSettings()
        super().__init__(self.get_user_interface(), "Node Mailer: Settings...")

    def get_user_interface(self) -> QtWidgets.QWidget:
        """Returns the user interface for the settings window."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        settings_label = QtWidgets.QLabel("Customize settings")
        settings_label.setStyleSheet("font-size: 18px;")
        settings_label.setStyle(NoShadowStyle())
        layout.addWidget(settings_label)

        divider_line = QtWidgets.QFrame()
        divider_line.setFrameShape(QtWidgets.QFrame.HLine)
        divider_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(divider_line)

        layout.addWidget(self.get_username_widget())
        layout.addWidget(self.get_audio_enabled_widget())
        layout.addStretch()
        layout.addWidget(self.get_bottom_buttons())

        return widget

    def get_username_widget(self) -> QtWidgets.QWidget:
        """Returns the username edit widget."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 10)
        widget.setLayout(layout)

        layout.addWidget(QtWidgets.QLabel("Username:"))
        self.username_lineedit = QtWidgets.QLineEdit()
        self.username_lineedit.setText(
            self.settings.value(SettingStrings.CUSTOM_USERNAME.value, os.getlogin())
        )
        self.username_lineedit.textChanged.connect(self.on_username_changed)
        self.username_lineedit.setStyleSheet("""
            background-color: white;
            selection-color: white;
        """)
        set_correct_highlight_color(self.username_lineedit, "#000BAB")

        layout.addWidget(self.username_lineedit)
        return widget

    def get_audio_enabled_widget(self) -> QtWidgets.QWidget:
        """Returns the audio enabled checkbox widget."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        layout.addWidget(QtWidgets.QLabel("Sound effects enabled:"))
        self.audio_checkbox = QtWidgets.QCheckBox()
        self.audio_checkbox.setStyleSheet(
            "QCheckBox::indicator { background-color: white; }"
        )
        checked = bool(
            self.settings.value(SettingStrings.AUDIO_ENABLED.value, True)
        )  # Qt stores boolean values as an integer in a string
        self.audio_checkbox.setChecked(checked)
        self.audio_checkbox.stateChanged.connect(self.on_audio_enabled_changed)
        set_checkbox_styling(self.audio_checkbox)

        layout.addWidget(self.audio_checkbox)
        return widget

    def get_bottom_buttons(self) -> QtWidgets.QWidget:
        """Returns the bottom buttons for the settings menu.

        Returns:
            The widget with the bottom buttons.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignRight)
        widget.setLayout(layout)

        ignore_button = NodeMailerButton("Close")
        ignore_button.clicked.connect(self.close)
        layout.addWidget(ignore_button)

        return widget

    def on_username_changed(self, new_username: str) -> None:
        """Called when the username is changed."""
        if new_username == "":
            new_username = os.getlogin()

        self.settings.setValue(SettingStrings.CUSTOM_USERNAME.value, new_username)

    def on_audio_enabled_changed(self, state: int) -> None:
        """Called when the audio enabled checkbox is changed."""
        self.settings.setValue(SettingStrings.AUDIO_ENABLED.value, bool(state))
