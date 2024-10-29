"""Code that controls all parts of the Node Mailer. Think of stuff like
starting background processes, connecting slots and signals, etc.

Written by Mervin van Brakel, 2024."""

from PySide2 import QtCore

from .networking.discovery import MailingClientsDiscovery


class NodeMailerController:
    """"""

    def __init__(self):
        print("[BreakTools] Starting Node Mailer background service...")
        self.start_background_tasks()

    def start_background_tasks(self) -> None:
        self.discovery = MailingClientsDiscovery()
