"""Windows 95 styled button widget.

Written by Mervin van Brakel, 2024."""

from pathlib import Path

from PySide2 import QtCore, QtGui, QtWidgets


class NodeMailerButton(QtWidgets.QPushButton):
    """Window 95 styled button!"""

    def __init__(self, text: str) -> None:
        """Initializes the button.

        Args:
            text: The text to display on the button.
        """
        super().__init__()
        self.configure_styling(text)
        self.connect_icon_changing_signals()

    def configure_styling(self, text: str) -> None:
        """Loads the icons and sets the button styling.

        Args:
            text: The text to display on the button.
        """
        self.button_icon = QtGui.QIcon(
            str(Path(__file__).parent.parent / "resources" / "button.png")
        )
        self.pressed_button_icon = QtGui.QIcon(
            str(Path(__file__).parent.parent / "resources" / "button_pressed.png")
        )
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setContentsMargins(0, 0, 0, 0)
        self.setIconSize(QtCore.QSize(80, 24))
        self.active_icon = self.button_icon
        self.setText(text)
        self.setStyleSheet("background: transparent; border: none; font: 11pt 'W95FA';")
        self.setFixedSize(80, 24)

    def connect_icon_changing_signals(self) -> None:
        """Connects the signals so the icon changes when needed."""
        self.pressed.connect(self.change_icon_to_pressed)
        self.released.connect(self.change_icon_to_normal)

    def change_icon_to_pressed(self) -> None:
        """Changes the icon to make the button look pressed."""
        self.active_icon = self.pressed_button_icon
        self.repaint()

    def change_icon_to_normal(self) -> None:
        """Changes the icon to make the button look normal."""
        self.active_icon = self.button_icon
        self.repaint()

    def paintEvent(self, _) -> None:  # noqa: N802
        """Overwrites the default paint event to draw our button text
        on top of our custom button icons."""
        painter = QtGui.QPainter(self)
        icon_rect = self.rect()
        icon = self.active_icon.pixmap(self.iconSize())
        painter.drawPixmap(icon_rect, icon)

        painter.setPen(QtGui.QPen(QtCore.Qt.black))
        painter.setFont(self.font())
        text_rect = self.rect()
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, self.text())
