"""All the code responsible for interfacing with Nuke. Yes this whole Nuke plugin only has 2 lines
of code that use the Nuke API lol."""

import tempfile
from pathlib import Path

import nuke


def get_selected_nodes_as_string() -> str:
    """Writes the selected nodes to a temp .nk file and returns its contents.

    Returns:
        list: The selected nodes.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_nuke_file = Path(temp_dir) / "nodes.nk"
        nuke.nodeCopy(str(temp_nuke_file))
        return temp_nuke_file.read_text()


def paste_nodes_from_string(node_string: str):
    """Takes the string, writes it as a temp .nk file and imports it.

    Args:
        node_string: The string containing the nodes.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_nuke_file = Path(temp_dir) / "nodes.nk"
        temp_nuke_file.write_text(node_string)
        nuke.nodePaste(str(temp_nuke_file))
