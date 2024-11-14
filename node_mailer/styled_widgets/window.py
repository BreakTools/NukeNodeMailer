"""Windows 95 styled parent window widget.

Written by Mervin van Brakel, 2024."""

from pathlib import Path

from PySide2 import QtCore, QtGui, QtWidgets

from node_mailer.styled_widgets.utility import NoShadowStyle


class NodeMailerWindow(QtWidgets.QWidget):
    """Base window class that looks like Windows 95."""

    def __init__(self, widget_to_display: QtWidgets.QWidget, window_title: str) -> None:
        """Initializes the stylized Node Mailer window class.

        Args:
            widget_to_display: The widget to display in the window.
            window_title: The title of the window.
        """
        super().__init__()
        self.configure_user_interface(widget_to_display, window_title)
        self.setWindowFlags(
            QtCore.Qt.Window
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
        )
        self.configure_custom_dragging_and_resizing()

        self.setWindowTitle(window_title)
        self.setWindowIcon(
            QtGui.QIcon(
                str(Path(__file__).parent.parent / "resources" / "node_mailer_icon")
            )
        )

    def configure_user_interface(
        self, widget_to_display: QtWidgets.QWidget, window_title: str
    ) -> None:
        """Configures the user interface with the given widget.

        Args:
            widget_to_display: The widget to display in the window.
            window_title: The title of the window.
        """
        self.store_button_icons()
        self.setStyleSheet(
            "background-color: #C0C0C0; font: 11pt 'W95FA'; color: black; text-shadow: none;"
        )
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.get_menu_bar_widget(window_title))
        layout.addWidget(widget_to_display)
        self.setStyle(NoShadowStyle())
        self.setLayout(layout)

    def store_button_icons(self) -> None:
        """Stores the icons for the buttons in the window so we can easily switch
        without having to read the files every time."""
        self.minimize_button_icon = QtGui.QIcon(
            str(Path(__file__).parent.parent / "resources" / "minimize_button.png")
        )
        self.minimize_button_pressed_icon = QtGui.QIcon(
            str(
                Path(__file__).parent.parent
                / "resources"
                / "minimize_button_pressed.png"
            )
        )
        self.maximize_button_icon = QtGui.QIcon(
            str(Path(__file__).parent.parent / "resources" / "maximize_button.png")
        )
        self.maximize_button_pressed_icon = QtGui.QIcon(
            str(
                Path(__file__).parent.parent
                / "resources"
                / "maximize_button_pressed.png"
            )
        )
        self.close_button_icon = QtGui.QIcon(
            str(Path(__file__).parent.parent / "resources" / "close_button.png")
        )

    def configure_custom_dragging_and_resizing(self) -> None:
        """Configures our custom logic for moving and scaling the window."""
        self.setMouseTracking(True)
        self.last_mouse_click_x_coordinate = 0
        self.last_mouse_click_y_coordinate = 0
        self.currently_moving_window = False
        self.currently_resizing_window = False

    def get_menu_bar_widget(self, window_title: str) -> QtWidgets.QWidget:
        """Creates the menu bar widget with all our stylized stuff in it.

        Args:
            window_title: The title of the window to display next to the Node Mailer icon.

        Returns:
            The menu bar widget.
        """
        menu_bar = QtWidgets.QWidget()
        menu_bar.setMouseTracking(True)
        menu_bar.setStyleSheet(
            "background-color: #000080; color: white; font: 11pt 'W95FA'; border: none;"
        )
        menu_bar.setStyle(NoShadowStyle())
        menu_bar_layout = QtWidgets.QHBoxLayout()
        menu_bar_layout.setSpacing(0)
        menu_bar_layout.setContentsMargins(3, 3, 3, 3)
        menu_bar.setLayout(menu_bar_layout)

        menu_bar_layout.addWidget(self.get_node_mailer_icon())
        menu_bar_layout.addWidget(QtWidgets.QLabel(window_title))
        menu_bar_layout.addStretch()
        menu_bar_layout.addWidget(self.get_minimize_button())
        menu_bar_layout.addWidget(self.get_maximize_button())
        menu_bar_layout.addWidget(self.get_close_button())

        return menu_bar

    def get_node_mailer_icon(self) -> QtWidgets.QLabel:
        """Creates the Node Mailer icon. Fun fact: This icon is called 'network neighborhood' in Windows 95.

        Returns:
            The Node Mailer icon.
        """
        icon = QtWidgets.QLabel()
        icon.setPixmap(
            QtGui.QPixmap(
                str(Path(__file__).parent.parent / "resources" / "node_mailer_icon.png")
            )
        )
        icon.setContentsMargins(0, 0, 0, 0)
        return icon

    def get_minimize_button(self) -> QtWidgets.QPushButton:
        """Creates the stylized and connected minimize button.

        Returns:
            The minimize button.
        """
        minimize_button = QtWidgets.QPushButton()
        minimize_button.setFocusPolicy(QtCore.Qt.NoFocus)
        minimize_button.setContentsMargins(0, 0, 0, 0)
        minimize_button.setIcon(self.minimize_button_icon)
        minimize_button.setIconSize(QtCore.QSize(16, 16))
        minimize_button.clicked.connect(self.showMinimized)
        minimize_button.pressed.connect(
            lambda: minimize_button.setIcon(self.minimize_button_pressed_icon)
        )
        minimize_button.released.connect(
            lambda: minimize_button.setIcon(self.minimize_button_icon)
        )
        return minimize_button

    def get_maximize_button(self) -> QtWidgets.QPushButton:
        """Creates the stylized and connected maximize button.

        Returns:
            The maximize button.
        """
        maximize_button = QtWidgets.QPushButton()
        maximize_button.setFocusPolicy(QtCore.Qt.NoFocus)
        maximize_button.setContentsMargins(0, 0, 0, 0)
        maximize_button.setIcon(self.maximize_button_icon)
        maximize_button.clicked.connect(self.showMaximized)
        maximize_button.pressed.connect(
            lambda: maximize_button.setIcon(self.maximize_button_pressed_icon)
        )
        maximize_button.released.connect(
            lambda: maximize_button.setIcon(self.maximize_button_icon)
        )
        return maximize_button

    def get_close_button(self) -> QtWidgets.QPushButton:
        """Creates the stylized and connected close button. I've looked at some old video recordings and
        it seems the close button didn't have any pressed animation, so that why only the minimize and maximize
        buttons have those!

        Returns:
            The close button.
        """
        close_button = QtWidgets.QPushButton()
        close_button.setFocusPolicy(QtCore.Qt.NoFocus)
        close_button.setContentsMargins(0, 0, 0, 0)
        close_button.setIcon(self.close_button_icon)
        close_button.clicked.connect(self.close)
        return close_button

    def is_mouse_on_menu_bar(self, event) -> bool:
        """Checks if the mouse is located on the menu bar so we know we should move the window.

        Args:
            event: The mouse event.

        Returns:
            If the mouse is on the menu bar.
        """
        if event.x() < 5 or event.x() > self.width() - 60:
            return False

        return 5 < event.y() < 25

    def is_mouse_on_bottom_right_corner(self, event) -> bool:
        """Checks if the mouse is located on the bottom right corner so we know we can resize the window.

        Args:
            event: The mouse event.

        Returns:
            If the mouse is on the bottom right corner.
        """
        return event.x() > self.width() - 10 and event.y() > self.height() - 10

    def update_cursor_icon(self, event) -> None:
        """Updates the cursor icon based on the position of the cursor in our window.

        Args:
            event: The mouse event.
        """
        if self.is_mouse_on_menu_bar(event):
            self.setCursor(QtCore.Qt.SizeAllCursor)
        elif self.is_mouse_on_bottom_right_corner(event):
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        """Processes the mouse press event for handling dragging and resize logic.

        Args:
            event: The mouse event.
        """
        self.last_mouse_click_x_coordinate = event.x()
        self.last_mouse_click_y_coordinate = event.y()

        if self.is_mouse_on_menu_bar(event):
            self.currently_moving_window = True

        if self.is_mouse_on_bottom_right_corner(event):
            self.currently_resizing_window = True

    def mouseReleaseEvent(self, _) -> None:  # noqa: N802
        """Processes the mouse release event for stopping the dragging/resizing of the window."""
        self.currently_moving_window = False
        self.currently_resizing_window = False

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        """Processes the mouse move event for dragging the window to another place based on the difference
        between the last known clicked x and y coordinates. Also handles resizing the window based on the current mouse position.

        Args:
            event: The mouse event.
        """
        self.update_cursor_icon(event)

        if self.currently_moving_window:
            self.move(
                event.globalX() - self.last_mouse_click_x_coordinate,
                event.globalY() - self.last_mouse_click_y_coordinate,
            )

        if self.currently_resizing_window:
            self.resize(event.x(), event.y())
