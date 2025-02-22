"""Test the houdini_toolbox.nodes.parameters module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party
import pytest

# Houdini Toolbox
import houdini_toolbox.nodes.parameters

# Houdini
import hou


# Need to ensure the hip file gets loaded.
pytestmark = pytest.mark.usefixtures("load_module_test_file")


# =============================================================================
# TESTS
# =============================================================================


def test_find_parameters_using_variable():
    """Test houdini_toolbox.nodes.parameters.find_parameters_using_variable."""
    result = houdini_toolbox.nodes.parameters.find_parameters_using_variable("BAR")

    assert result == ()

    expected = (
        hou.parm("/obj/geo1/font1/text"),
        hou.parm("/out/mantra1/vm_picture"),
        hou.parm("/out/mantra1/soho_diskfile"),
        hou.parm("/out/mantra1/vm_dcmfilename"),
        hou.parm("/out/mantra1/vm_dsmfilename"),
        hou.parm("/out/mantra1/vm_tmpsharedstorage"),
        hou.parm("/stage/rendergallerysource"),
        hou.parm("/tasks/topnet1/taskgraphfile"),
        hou.parm("/tasks/topnet1/localscheduler/pdg_workingdir"),
    )

    result = houdini_toolbox.nodes.parameters.find_parameters_using_variable("HIP")

    assert result == expected

    expected = (
        hou.parm("/out/mantra1/vm_picture"),
        hou.parm("/stage/rendergallerysource"),
        hou.parm("/tasks/topnet1/taskgraphfile"),
        hou.parm("/tasks/topnet1/localscheduler/tempdircustom"),
    )

    result = houdini_toolbox.nodes.parameters.find_parameters_using_variable("$HIPNAME")

    assert result == expected

    expected = (hou.parm("/obj/geo1/font2/text"),)

    result = houdini_toolbox.nodes.parameters.find_parameters_using_variable("$HIPFILE")

    assert result == expected

    expected = (
        hou.parm("/obj/geo1/font1/text"),
        hou.parm("/tasks/topnet1/taskgraphfile"),
    )

    result = houdini_toolbox.nodes.parameters.find_parameters_using_variable("F")

    assert result == expected

    expected = (hou.parm("/out/mantra1/vm_picture"),)

    result = houdini_toolbox.nodes.parameters.find_parameters_using_variable("$F4")

    assert result == expected


def test_find_parameters_with_value():
    """Test houdini_toolbox.nodes.parameters.find_parameters_with_value."""
    result = houdini_toolbox.nodes.parameters.find_parameters_with_value("gaussian")
    assert result == (hou.parm("/out/mantra1/vm_pfilter"),)

    result = houdini_toolbox.nodes.parameters.find_parameters_with_value("render1")
    assert result == ()

    result = houdini_toolbox.nodes.parameters.find_parameters_with_value("render")
    assert result == (
        hou.parm("/obj/geo1/font1/text"),
        hou.parm("/out/mantra1/vm_picture"),
    )

    result = houdini_toolbox.nodes.parameters.find_parameters_with_value("renders")
    assert result == (hou.parm("/obj/geo1/font2/text"),)
