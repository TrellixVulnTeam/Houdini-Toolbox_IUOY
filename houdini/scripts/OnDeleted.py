"""Perform tasks when a Houdini node is deleted."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox
from houdini_toolbox.events import NodeEvents, run_event

# =============================================================================
# FUNCTIONS
# =============================================================================


def main():
    """Main function."""
    run_event(NodeEvents.OnDeleted, kwargs)  # pylint: disable=undefined-variable


# =============================================================================

main()
