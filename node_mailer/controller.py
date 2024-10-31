"""Code that controls all parts of the Node Mailer. Think of stuff like
starting background processes, connecting slots and signals, etc.

Written by Mervin van Brakel, 2024."""

from PySide2 import QtCore

from .networking.discovery import ClientDiscoveryModel


class NodeMailerController:
    """"""

    def __init__(self):
        print("[BreakTools] Starting Node Mailer background service...")
        self.initialize_models()

    def initialize_models(self) -> None:
        self.discovery_model = ClientDiscoveryModel()
