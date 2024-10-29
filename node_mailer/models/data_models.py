"""Dataclasses for Node Mailer.

Written by Mervin van Brakel, 2024."""

from dataclasses import dataclass


@dataclass
class NodeMailerClient:
    """A node mailer client that is available on the local network."""

    name: str
    ip_address: str
