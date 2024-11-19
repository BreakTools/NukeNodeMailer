"""Dataclasses for Node Mailer.

Written by Mervin van Brakel, 2024."""

import json
from dataclasses import asdict, dataclass

from PySide2 import QtNetwork


@dataclass
class NodeMailerClient:
    """A node mailer client that is available on the local network."""

    name: str
    ip_address: str
    favorite: bool
    last_seen_timestamp: float


@dataclass
class NodeMailerMail:
    """A message that is sent between two node mailer clients."""

    sender_name: str
    message: str
    node_string: str
    timestamp: int

    def as_json(self) -> str:
        """Returns the message as a JSON string."""
        return json.dumps(asdict(self))


@dataclass
class ReceivingConnection:
    """An open TCP connection that is actively sending a message."""

    socket: QtNetwork.QTcpSocket
    message: str
