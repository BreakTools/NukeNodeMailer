"""All the code responsible for interfacing with Nuke. Yes this whole Nuke plugin only has 3 lines
of code that actually use the Nuke API lol.

Written by Mervin van Brakel, 2024."""

import base64
import tempfile
from pathlib import Path
from typing import Union

import nuke

from node_mailer.data_models import NodeMailerMail


def get_selected_nodes_as_encoded_string() -> Union[str, None]:
    """Writes the selected nodes to a temp .nk file and returns its contents in a base64 encoded string.

    Returns:
        The selected nodes as an encoded string or None if no nodes are selected.
    """
    if not nuke.selectedNodes():
        return None

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_nuke_file = Path(temp_dir) / "nodes.nk"
        nuke.nodeCopy(str(temp_nuke_file))
        node_string = temp_nuke_file.read_text()
        return base64.b64encode(node_string.encode("ascii")).decode("ascii")


def paste_nodes_from_encoded_string(encoded_node_string: str) -> None:
    """Takes the base64 encoded string, decodes it, writes it as a temp .nk file and imports it.

    Args:
        The string containing the nodes.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        decoded_node_string = base64.b64decode(
            encoded_node_string.encode("ascii")
        ).decode("ascii")
        temp_nuke_file = Path(temp_dir) / "nodes.nk"
        temp_nuke_file.write_text(decoded_node_string)
        nuke.nodePaste(str(temp_nuke_file))


def import_mail(mail: NodeMailerMail) -> None:
    """Imports the nodes from the mail into the current Nuke session.

    Args:
        mail: The mail to import.
    """
    paste_nodes_from_encoded_string(mail.node_string)
