"""All the code responsible for interfacing with Nuke. Yes this whole Nuke plugin only has 2 lines
of code that use the Nuke API lol."""

import base64
import tempfile
from pathlib import Path

import nuke


def get_selected_nodes_as_encoded_string() -> str:
    """Writes the selected nodes to a temp .nk file and returns its contents in an encoded string.

    Returns:
        The selected nodes.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_nuke_file = Path(temp_dir) / "nodes.nk"
        nuke.nodeCopy(str(temp_nuke_file))
        node_string = temp_nuke_file.read_text()
        return base64.b64encode(node_string.encode("ascii")).decode("ascii")


def paste_nodes_from_encoded_string(encoded_node_string: str):
    """Takes the string, decodes it, writes it as a temp .nk file and imports it.

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
