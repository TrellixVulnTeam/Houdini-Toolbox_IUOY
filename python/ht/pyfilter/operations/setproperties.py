"""This module contains an operation to set properties passed as a string or
file path.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from collections import Iterable
import json

# Houdini Toolbox Imports
from ht.logger import logger
from ht.pyfilter.operations.operation import PyFilterOperation, log_filter
from ht.pyfilter.property import get_property, set_property

# =============================================================================
# CLASSES
# =============================================================================

class PropertySetterManager(object):
    """Class for creating and managing PropertySetters.

    """

    def __init__(self):
        self._properties = {}

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _load_from_data(self, data):
        """Build PropertySetter objects from data.

        :param data: A data dictionary.
        :type data: dict
        :return:

        """
        # Process each filter stage name and it's data.
        for stage_name, stage_data in data.iteritems():
            # A list of properties for this stage.
            properties = self.properties.setdefault(stage_name, [])

            # Check if the stage should be disabled.
            if "disabled" in stage_data:
                if stage_data["disabled"]:
                    logger.debug(
                        "Stage entry disabled: {}".format(stage_name)
                    )

                    continue

                # If not, remove the disabled entry.
                del(stage_data["disabled"])

            # The data is stored by property name.
            for property_name, property_block in stage_data.iteritems():
                # Wrapping properties in a 'rendertype:type' block is supported
                # if the the name indicates that we have to modify the data.
                if property_name.startswith("rendertype:"):
                    # Get the rendertype name.
                    rendertype = property_name.split(":")[1]

                    # Process each child property block.
                    for name, block in property_block.iteritems():
                        # If the child data is the standard dictionary of data
                        # we can just insert the rendertype value into it.
                        if isinstance(block, dict):
                            block["rendertype"] = rendertype

                        # If the child data is a list of dictionaries then
                        # iterate over each one and insert the value.
                        elif isinstance(block, list):
                            for item in block:
                                item["rendertype"] = rendertype

                        # Process the child data block.
                        _process_block(
                            properties, stage_name, name, block
                        )

                # Normal data.
                else:
                    _process_block(
                        properties, stage_name, property_name, property_block
                    )

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def properties(self):
        """dict: Dictionary containing properties."""
        return self._properties

    # =========================================================================
    # METHODS
    # =========================================================================

    def load_from_file(self, file_path):
        """Load properties from a file.

        :param file_path: A file containing json property data.
        :type file_path: str
        :return:

        """
        logger.debug("Reading properties from {}".format(file_path))

        # Load json data from the file.
        with open(file_path) as f:
            data = json.load(f)

        self._load_from_data(data)

    def parse_from_string(self, property_string):
        """Load properties from a string.

        :param property_string: A json string containing property data.
        :type property_string: str

        """
        data = json.loads(property_string)

        self._load_from_data(data)

    def set_properties(self, stage):
        """Apply properties.

        :param stage: The stage name.
        :type stage: str
        :return:

        """
        if stage in self.properties:
            for prop in self.properties[stage]:
                prop.setProperty()


class PropertySetter(object):
    """An object representing a Mantra property being set by PyFilter.

    :param name: The property name.
    :type name: str
    :param property_block: Property data to set.
    :type property_block: dict

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, name, property_block):
        self._name = name

        # Store the raw value object.
        self._value = property_block["value"]

        self._enabled = True
        self._find_file = False
        self._rendertype = None

        if "findfile" in property_block:
            self.find_file = property_block["findfile"]

        if "enabled" in property_block:
            self.enabled = property_block["enabled"]

        if "rendertype" in property_block:
            self.rendertype = property_block["rendertype"]

        # Perform any value cleanup.
        self._process_value()

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        value = self.value

        # Wrap string values in single quotes.
        if isinstance(value, str):
            value = "'{}'".format(value)

        return "<PropertySetter {}={}>".format(self.name, value)

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _process_value(self):
        """Perform operations and cleanup of the value data.

        :return:

        """
        import hou

        # Skip normal types.
        if isinstance(self.value, (bool, float, int)):
            return

        # Don't do anything if the property isn't enabled.
        if not self.enabled:
            return

        # If the object is a list of only one entry, extract it.
        if len(self.value) == 1:
            self.value = self.value[0]

        # If the value is actually a relative file, search for it in the
        # Houdini path.
        if self.find_file:
            self.value = hou.findFile(self.value)

        # Object is a list (possibly numbers or strings or both).
        if isinstance(self.value, list):
            # Does the list contain any strings.
            contains_string = False

            for val in self.value:
                # If the value is a string, flag it.
                if isinstance(val, str):
                    contains_string = True
                    break

            # If at least one value is a string then we need to convert them
            # all to strings.
            if contains_string:
                self.value = [str(val) for val in self.value]

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def enabled(self):
        """bool: Is the property setting enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled

    # =========================================================================

    @property
    def find_file(self):
        """bool: Is the value the name of a file to find."""
        return self._find_file

    @find_file.setter
    def find_file(self, find_file):
        self._find_file = find_file

    # =========================================================================

    @property
    def name(self):
        """str: The name of the property to set."""
        return self._name

    # =========================================================================

    @property
    def rendertype(self):
        """str: Apply to specific render types."""
        return self._rendertype

    @rendertype.setter
    def rendertype(self, rendertype):
        self._rendertype = rendertype

    # =========================================================================

    @property
    def value(self):
        """object: The value to set the property."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    # =========================================================================
    # METHODS
    # =========================================================================

    def set_property(self):
        """Set the property to the value.

        :return:

        """
        import hou

        # Don't do anything if the property isn't enabled.
        if not self.enabled:
            return

        # Is this property being applied to a specific render type.
        if self.rendertype is not None:
            # Get the rendertype for the current pass.
            rendertype = get_property("renderer:rendertype")

            # If the type pattern doesn't match, abort.
            if not hou.patternMatch(self.rendertype, rendertype):
                return

        logger.debug(
            "Setting property '{}' to {}".format(self.name, self.value)
        )

        # Update the property value.
        set_property(self.name, self.value)


class MaskedPropertySetter(PropertySetter):
    """A PropertySetter that supports masking against other properties.

    :param name: The name of the property to set.
    :type name: str
    :param property_block: Property data to set.
    :type property_block: dict
    :param mask_property_name: The name of the mask property.
    :type mask_property_name: str

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, name, property_block, mask_property_name):
        super(MaskedPropertySetter, self).__init__(name, property_block)

        # Look for a mask property.
        self._mask = str(property_block["mask"])

        self._mask_property_name = mask_property_name

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        value = self.value

        # Wrap string values in single quotes.
        if isinstance(value, str):
            value = "'{}'".format(value)

        return "<{} {}={} mask='{}'>".format(
            self.__class__.__name__,
            self.name,
            value,
            self.mask
        )

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def mask(self):
        """str: A mask value."""
        return self._mask

    @property
    def mask_property_name(self):
        """str: The property name to compare the mask against."""
        return self._mask_property_name

    # =========================================================================
    # METHODS
    # =========================================================================

    def set_property(self):
        """Set the property under mantra.

        :return:

        """
        import hou

        # Is this property being applied using a name mask.
        if self.mask is not None:
            # Get the name of the item that is currently being filtered.
            filtered_item = get_property(self.mask_property_name)

            # If the mask pattern doesn't match, abort.
            if not hou.patternMatch(self.mask, filtered_item):
                return

        # Call the super class function to set the property.
        super(MaskedPropertySetter, self).set_property()


class SetProperties(PyFilterOperation):
    """Operation to set misc properties passed along as a string or file path.

    :param manager: The manager this operation is registered with.
    :type manager: ht.pyfilter.manager.PyFilterManager

    """

    def __init__(self, manager):
        super(SetProperties, self).__init__(manager)

        self._property_manager = PropertySetterManager()

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def property_manager(self):
        """PropertySetterManager:Get the property manager."""
        return self._property_manager

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def build_arg_string(properties=None, properties_file=None):
        """Build an argument string for this operation.

        'properties' should be a json compatible dictionary.

        :param properties: The property data to set.
        :type properties: dict
        :param properties_file: A file to set property values from.
        :type properties_file: str
        :return: The constructed argument string.
        :rtype: str

        """
        args = []

        if properties is not None:
            args.append(
                '--properties="{}"'.format(
                    json.dumps(properties).replace('"', '\\"')
                )
            )

        if properties_file is not None:
            args.append("--properties-file={}".format(properties_file))

        return " ".join(args)

    @staticmethod
    def register_parser_args(parser):
        """Register interested parser args for this operation.

        :param parser: The argument parser to attach arguements to.
        :type parser: argparse.ArgumentParser.
        :return:

        """
        parser.add_argument(
            "--properties",
            nargs=1,
            action="store",
            help="Specify a property dictionary on the command line."
        )

        parser.add_argument(
            "--properties-file",
            nargs=1,
            action="store",
            help="Use a file to define render properties to override.",
            dest="properties_file"
        )

    # =========================================================================
    # METHODS
    # =========================================================================

    @log_filter
    def filterCamera(self):
        """Apply camera properties.

        :return:

        """
        self.property_manager.set_properties("camera")

    @log_filter("object:name")
    def filterInstance(self):
        """Apply object properties.

        :return:

        """
        self.property_manager.set_properties("instance")

    @log_filter("object:name")
    def filterLight(self):
        """Apply light properties.

        :return:

        """
        self.property_manager.set_properties("light")

    def process_parsed_args(self, filter_args):
        """Process any parsed args that the operation may be interested in.

        :param filter_args: The argparse namespace containing processed args.
        :type filter_args: argparse.Namespace
        :return:

        """
        if filter_args.properties is not None:
            for prop in filter_args.properties:
                self.property_manager.parse_from_string(prop)

        if filter_args.properties_file is not None:
            for file_path in filter_args.properties_file:
                self.property_manager.load_from_file(file_path)

    def should_run(self):
        """Determine whether or not this filter should be run.

        This operations runs if there are properties to set.

        :return: Whether or not this operation should run.
        :rtype: bool

        """
        return any(self.property_manager.properties)

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _create_property_setter(stage_name, property_name, property_block):
    """Create a PropertySetter based on data.

    :param stage_name: The filter stage to run for.
    :type stage_name: str
    :param property_name: The name of the property to set.
    :type property_name: str
    :param property_block: The property data to set.
    :type property_block: dict
    :return: A property setter object.
    :rtype: PropertySetter

    """
    # Handle masked properties.
    if "mask" in property_block:
        # Filter a plane.
        if stage_name == "plane":
            return MaskedPropertySetter(
                property_name,
                property_block,
                "plane:variable"
            )

        # Something involving an actual object.
        elif stage_name in ("fog", "light", "instance"):
            return MaskedPropertySetter(
                property_name,
                property_block,
                "object:name"
            )

        # If masking is specified but we don't know how to handle it, log a
        # warning message.  We will still return a regular PropertySetter
        # object though.
        else:
            logger.warning(
                "No masking available for {}:{}.".format(
                    stage_name,
                    property_name
                )
            )

    # Generic property setter.
    return PropertySetter(property_name, property_block)


def _process_block(properties, stage_name, name, block):
    """Process a data block to add properties.

    :param properties: A list of property settings.
    :type properties: list
    :param stage_name: The filter stage to run for.
    :type stage_name: str
    :param name: The name of the property to set.
    :type name: str
    :param block: The property data to set.
    :type block: dict|list(dict)

    """
    # If we want to set the same property with different settings multiple
    # times (eg. different masks) we can have a list of objects instead.
    # In the case where we just have a single one (really a dictionary)
    # then add it to a list so we can process it in a loop.
    if isinstance(block, dict):
        block = [block]

    # (Can't remember why this check is here. Shouldn't be needed, right?)
    if isinstance(block, Iterable):
        # Process any properties in the block.
        for property_elem in block:
            prop = _create_property_setter(
                stage_name,
                name,
                property_elem
            )

            properties.append(prop)
