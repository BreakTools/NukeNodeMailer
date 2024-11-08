"""Constants for Node Mailer, like strings and enums.

Written by Mervin van Brakel, 2024."""

from enum import Enum


class Ports(Enum):
    """Port numbers used by Node Mailer."""

    BROADCAST = 37220
    MESSAGING = 37221


class SettingStrings(Enum):
    """Enum that stores setting strings for use with QSettings."""

    FAVORITES = "node_mailer/favorites"
