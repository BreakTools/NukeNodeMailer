import nuke

import node_mailer


def create_mailer_menu() -> None:
    """Adds the Node Mailer menu to the Nuke menubar."""
    menubar = nuke.menu("Nuke")
    mailer_menu = menubar.addMenu("Node Mailer")

    mailer_menu.addCommand(
        "Mail Nodes",
        "global node_mailer_controller;node_mailer_controller.open_mailing_window()",
        "",
    )
    mailer_menu.addCommand(
        "Mail History",
        "global node_mailer_controller;node_mailer_controller.open_history_window()",
        "",
    )
    mailer_menu.addCommand("-", "", "")
    mailer_menu.addCommand(
        "About...",
        "global node_mailer_controller;node_mailer_controller.open_about_window()",
        "",
    )


def start_node_mailer() -> None:
    """Starts background processes for the Node Mailer."""
    global node_mailer_controller
    node_mailer_controller = node_mailer.controller.NodeMailerController()


create_mailer_menu()
start_node_mailer()
