"""Code that controls all parts of the Node Mailer. Think of stuff like
starting background processes, connecting slots and signals, etc.

Written by Mervin van Brakel, 2024."""

from pathlib import Path

from PySide2 import QtCore, QtGui

from .models.history_storage import HistoryStorage
from .networking.discovery import ClientDiscoveryModel
from .networking.messaging import DirectMessagingHandler


class NodeMailerController(QtCore.QObject):
    """Controller for Node Mailer, responsible for hooking up the models to the UI."""

    def __init__(self):
        print("[BreakTools] Starting Node Mailer background service...")
        self.initialize_systems()
        self.add_font_to_database()

    def initialize_systems(self) -> None:
        """Initializes all systems/models required for Node Mailer to function."""
        self.discovery_model = ClientDiscoveryModel()
        self.direct_messaging_handler = DirectMessagingHandler()
        self.history_storage_model = HistoryStorage()

    def add_font_to_database(self) -> None:
        """Adds our nice Windows 95 font to the Qt font database so we can use it
        in stylesheets."""
        QtGui.QFontDatabase.addApplicationFont(
            str(Path(__file__).parent / "resources" / "W95FA.otf")
        )
