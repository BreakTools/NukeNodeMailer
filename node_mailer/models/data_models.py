"""Dataclasses for Node Mailer.

Written by Mervin van Brakel, 2024."""

import json
from dataclasses import asdict, dataclass


@dataclass
class NodeMailerClient:
    """A node mailer client that is available on the local network."""

    name: str
    ip_address: str


@dataclass
class NodeMailerMail:
    """A message that is sent between two node mailer clients."""

    sender_name: str
    description: str
    node_string: str
    timestamp: int

    def as_json(self) -> str:
        """Returns the message as a JSON string."""
        return json.dumps(asdict(self))
