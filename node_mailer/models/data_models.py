"""Dataclasses for Node Mailer.

Written by Mervin van Brakel, 2024."""

import json
from dataclasses import dataclass


@dataclass
class NodeMailerClient:
    """A node mailer client that is available on the local network."""

    name: str
    ip_address: str


@dataclass
class NodeMailerMessage:
    """A message that is sent between two node mailer clients."""

    sender_name: str
    description: str
    node_string: str

    def as_json(self) -> str:
        """Returns the message as a JSON string."""
        return json.dumps(
            {
                "sender_name": self.sender_name,
                "description": self.description,
                "node_string": self.node_string,
            }
        )
