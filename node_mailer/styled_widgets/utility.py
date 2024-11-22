"""Utility classes for use in stylized widgets.

Written by Mervin van Brakel, 2024."""

from pathlib import Path

from PySide2 import QtGui, QtWidgets


class NoShadowStyle(QtWidgets.QProxyStyle):
    """So Nuke has this thing in its QStyle that adds a tiny drop shadow to
    all the text that's displayed. I think that when we set a custom stylesheet on a widget
    this default styling gets copied over, which is kinda annoying because Windows 95 had
    no such shadows. The fix is overriding the item text draw method on a custom style and
    adding that manually to any widget that has both text and a custom stylesheet.
    """

    def drawItemText(self, painter, rect, flags, pal, enabled, text, text_role):  # noqa: N802, PLR0913
        """Overrides the drawItemText method to remove the Nuke dropdown shadow."""
        if text_role == QtGui.QPalette.Text:
            pal.setColor(QtGui.QPalette.Text, pal.color(QtGui.QPalette.WindowText))

        super().drawItemText(painter, rect, flags, pal, enabled, text, text_role)


def set_correct_highlight_color(widget: QtWidgets.QWidget, hex_color: str) -> None:
    """Nuke seems to want to slap it's signature orange color onto everything the mouse selects.
    We shall not give into the orange. We must resist. We must fight back. We must paint it blue.

    Args:
        widget: The widget to set the highlight color on.
    """
    palette = widget.palette()
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(hex_color))
    widget.setPalette(palette)


def set_checkbox_styling(checkbox_widget: QtWidgets.QCheckBox) -> None:
    """Configures the styling for a checkbox widget.

    Args:
        checkbox_widget: The checkbox widget to style.
    """
    path_to_check_icon = str(
        Path(__file__).parent.parent / "resources" / "check.png"
    ).replace("\\", "/")
    checkbox_widget.setStyleSheet(
        f"""
        QCheckBox::indicator {{
            width: 12px;
            height: 12px;
            background-color: white;
            border: 1px solid #000000;
        }}
        QCheckBox::indicator:checked {{
            image: url({path_to_check_icon});
            width: 12px;
            height: 12px;
        }}
        """
    )
