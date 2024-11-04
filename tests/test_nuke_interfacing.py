"""Tests for the Nuke interfacing functions of Node Mailer."""

import base64

import nuke

from node_mailer.nuke_interfacing import (
    get_selected_nodes_as_encoded_string,
    paste_nodes_from_encoded_string,
)


def test_get_selected_nodes_as_string():
    """Test to see if nodes are correctly converted to a string."""
    nuke.createNode("Constant")
    nuke.createNode("Text")

    for node in nuke.allNodes():
        node["selected"].setValue(True)

    node_string = get_selected_nodes_as_encoded_string()
    node_string = base64.b64decode(node_string.encode("ascii")).decode("ascii")
    assert node_string.startswith("set cut_paste_input")
    assert "Constant" in node_string
    assert "Text1" in node_string


def test_paste_nodes_from_string():
    """Test to see if nodes from a string are pasted correctly."""
    test_string = """set cut_paste_input [stack 0]
    version 15.0 v1
    Constant {
    inputs 0
    channels rgb
    name Constant1
    selected true
    xpos -88
    ypos -228
    }
    Text1 {
    font_size_toolbar 100
    font_width_toolbar 100
    font_height_toolbar 100
    message Testing!
    old_message {{84 101 115 116 105 110 103 33}
    }
    box {885.5 753.5 1234.5 854.5}
    transforms {{0 2}
    }
    cursor_position 4
    center {1024 778}
    cursor_initialised true
    initial_cursor_position {{885.5 854.5}
    }
    group_animations {{0} imported: 0 selected: items: "root transform/"}
    animation_layers {{1 11 1024 778 0 0 1 1 0 0 0 0}
    }
    name Text1
    selected true
    xpos -88
    ypos -136
    }"""
    encoded_test_string = base64.b64encode(test_string.encode("ascii")).decode("ascii")
    paste_nodes_from_encoded_string(encoded_test_string)

    assert nuke.toNode("Constant1")
    assert nuke.toNode("Text1")
