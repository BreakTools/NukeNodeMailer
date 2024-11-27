"""Code that controls all parts of the Node Mailer. Think of stuff like
starting background processes, connecting slots and signals, etc.

Written by Mervin van Brakel, 2024."""

import os
from datetime import datetime
from pathlib import Path

from PySide2 import QtCore, QtGui

from . import nuke_interfacing
from .audio_handler import play_click_sound, play_you_got_mail
from .data_models import NodeMailerClient, NodeMailerMail
from .models.constants import ReceivedMailPopupOption, SettingStrings
from .models.discovery import ClientDiscovery
from .models.history_storage import HistoryStorage
from .models.messaging import DirectMessaging
from .user_interface.about import AboutWindow
from .user_interface.history import HistoryWindow
from .user_interface.mailing import MailingWindow
from .user_interface.popups import ReceivedMailPopup, display_error_popup
from .user_interface.settings import SettingsWindow


class NodeMailerController(QtCore.QObject):
    """Controller for Node Mailer, responsible for hooking up the models to the UI."""

    def __init__(self) -> None:
        print("[BreakTools] Starting Node Mailer background service...")
        super().__init__()
        self.initialize_systems()
        self.add_font_to_database()
        self.initialize_windows()
        self.connect_signals()

    def initialize_systems(self) -> None:
        """Initializes all systems/models required for Node Mailer to function."""
        self.discovery_model = ClientDiscovery()
        self.direct_messaging_model = DirectMessaging()
        self.history_storage_model = HistoryStorage()

    def add_font_to_database(self) -> None:
        """Adds our nice Windows 95 font to the Qt font database so we can use it
        in stylesheets."""
        QtGui.QFontDatabase.addApplicationFont(
            str(Path(__file__).parent / "resources" / "W95FA.otf")
        )

    def initialize_windows(self) -> None:
        """Initializes all windows required for Node Mailer."""
        self.mailing_window = MailingWindow(self.discovery_model)
        self.history_window = HistoryWindow(self.history_storage_model)
        self.settings_window = SettingsWindow()
        self.about_window = AboutWindow()

    def connect_signals(self) -> None:
        """Connects the signals of various components together."""
        self.history_window.import_mail.connect(nuke_interfacing.import_mail)
        self.mailing_window.send_mail.connect(self.send_mail)
        self.direct_messaging_model.message_received.connect(self.mail_received)

    def open_mailing_window(self) -> None:
        """Opens the mailing window."""
        self.mailing_window.show()
        play_click_sound()

    def open_history_window(self) -> None:
        """Opens the history window."""
        self.history_storage_model.retrieve_all_mail_from_database()
        self.history_window.show()
        play_click_sound()

    def open_settings_window(self) -> None:
        """Opens the settings window."""
        self.settings_window.show()
        play_click_sound()

    def open_about_window(self) -> None:
        """Opens the about window."""
        self.about_window.show()
        play_click_sound()

    def send_mail(self, client: NodeMailerClient, message: str) -> None:
        """Retrieves data from other systems and sends it off to the given client.

        Args:
            client: The client to send the mail to.
            message: The message
        """
        encoded_node_string = nuke_interfacing.get_selected_nodes_as_encoded_string()

        if not encoded_node_string:
            display_error_popup("You don't have any nodes selected to mail!")
            return

        unix_timestamp = int(datetime.now().timestamp())

        settings = QtCore.QSettings()
        mail = NodeMailerMail(
            sender_name=settings.value(
                SettingStrings.CUSTOM_USERNAME.value, os.getlogin()
            ),
            message=message,
            node_string=encoded_node_string,
            timestamp=unix_timestamp,
        )

        try:
            self.direct_messaging_model.send_mail_to_client(mail, client)
        except ConnectionError as error_message:
            display_error_popup(f"Error: {error_message}")
            return

        self.mailing_window.message_text_edit.clear()
        self.mailing_window.close()

    def mail_received(self, mail: NodeMailerMail) -> None:
        """Handles a received mail using the received mail popup.

        Args:
            mail: The mail that was received.
        """
        received_mail_popup = ReceivedMailPopup(mail)
        play_you_got_mail()
        received_mail_popup.exec_()

        if received_mail_popup.picked_option == ReceivedMailPopupOption.IGNORE:
            return

        self.history_storage_model.store_mail(mail)

        if received_mail_popup.picked_option == ReceivedMailPopupOption.IMPORT:
            nuke_interfacing.import_mail(mail)
