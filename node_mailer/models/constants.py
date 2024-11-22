"""Constants for the Node Mailer models. Think of Enums and configs and stuff.

Written by Mervin van Brakel, 2024."""

from enum import Enum


class MailHistoryRow(Enum):
    """Enum that stores mail history row mapping."""

    SENDER_NAME = (0, "Sender name", "sender_name")
    MESSAGE = (1, "Message", "message")
    TIMESTAMP = (2, "Timestamp", "timestamp")

    def __init__(
        self, column_index: int, display_name: str, dataclass_field: str
    ) -> None:
        self.column_index = column_index
        self.display_name = display_name
        self.dataclass_field = dataclass_field


class Ports(Enum):
    """Port numbers used by Node Mailer."""

    BROADCAST = 37220
    MESSAGING = 37221


class SettingStrings(Enum):
    """Enum that stores setting strings for use with QSettings."""

    FAVORITES = "node_mailer/favorites"
    CUSTOM_USERNAME = "node_mailer/custom_username"
    AUDIO_ENABLED = "node_mailer/audio_enabled"


class ReceivedMailPopupOption(Enum):
    """Enum that stores the options a user can pick in the received mail dialog."""

    IGNORE = "Ignore"
    SAVE = "Save"
    IMPORT = "Import"
