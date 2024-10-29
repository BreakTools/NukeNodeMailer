import os

import nuke

import node_mailer  # noqa: F401


def create_mailer_menu() -> None:
    """Adds the Node Mailer menu to the Nuke menubar."""
    menubar = nuke.menu("Nuke")
    mailer_menu = menubar.addMenu("Node Mailer")

    mailer_menu.addCommand(
        "Mail Nodes",
        "",
        "",
    )
    mailer_menu.addCommand(
        "Mail History",
        "",
        "",
    )
    mailer_menu.addCommand("-", "", "")
    mailer_menu.addCommand(
        "About...",
        "",
        "",
    )

    if os.environ.get("PIPELINE_DEVELOPER"):
        mailer_menu.addCommand(
            "Reload Node Mailer",
            "import importlib;importlib.reload(node_mailer)",
            "",
        )


def start_node_mailer() -> None:
    """Starts background processes for the Node Mailer."""
    global node_mailer_controller
    node_mailer_controller = node_mailer.controller.NodeMailerController()


create_mailer_menu()
start_node_mailer()
