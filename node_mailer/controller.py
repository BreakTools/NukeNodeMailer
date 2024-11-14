"""Code that controls all parts of the Node Mailer. Think of stuff like
starting background processes, connecting slots and signals, etc.

Written by Mervin van Brakel, 2024."""

from pathlib import Path

from PySide2 import QtCore, QtGui

from . import nuke_interfacing
from .models.discovery import ClientDiscovery
from .models.history_storage import HistoryStorage
from .models.messaging import DirectMessaging
from .user_interface.about import AboutWindow
from .user_interface.history import HistoryWindow
from .user_interface.mailing import MailingWindow


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
        self.mailing_window = MailingWindow()
        self.about_window = AboutWindow()
        self.history_window = HistoryWindow(self.history_storage_model)

    def connect_signals(self) -> None:
        """Connects the signals of various components together."""
        self.history_window.import_mail.connect(nuke_interfacing.import_mail)

    def open_mailing_window(self) -> None:
        """Opens the mailing window."""
        self.mailing_window.show()

    def open_history_window(self) -> None:
        """Opens the history window."""
        self.history_window.show()

    def open_about_window(self) -> None:
        """Opens the about window."""
        self.about_window.show()
