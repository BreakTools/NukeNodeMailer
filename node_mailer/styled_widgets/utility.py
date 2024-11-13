"""Utility classes for use in stylized widgets.

Written by Mervin van Brakel, 2024."""

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
