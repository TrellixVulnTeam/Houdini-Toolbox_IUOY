"""Tests for houdini_toolbox.ui.menus.opmenu module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox
import houdini_toolbox.ui.menus.opmenu

# Houdini
import hou

# =============================================================================
# TESTS
# =============================================================================


def test_create_absolute_reference_copy(mocker):
    """Test houdini_toolbox.ui.menus.opmenu.create_absolute_reference_copy."""
    mock_node = mocker.MagicMock(spec=hou.Node)

    scriptargs = {"node": mock_node}

    houdini_toolbox.ui.menus.opmenu.create_absolute_reference_copy(scriptargs)

    mock_node.parent.return_value.copyItems.assert_called_with(
        [mock_node], channel_reference_originals=True, relative_references=False
    )


def test_save_item_to_file(mocker):
    """Test houdini_toolbox.ui.menus.opmenu.save_item_to_file."""
    mock_copy = mocker.patch("houdini_toolbox.ui.menus.opmenu.copy_item")

    mock_node = mocker.MagicMock(spec=hou.Node)

    scriptargs = {"node": mock_node}

    houdini_toolbox.ui.menus.opmenu.save_item_to_file(scriptargs)

    mock_copy.assert_called_with(mock_node)
