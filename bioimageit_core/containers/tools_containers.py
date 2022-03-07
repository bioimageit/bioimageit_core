# -*- coding: utf-8 -*-
"""BioIMageIT tool containers.

This module contains containers for Tool info
and tool database

Methods
-------
PARAM_NUMBER
PARAM_STRING
PARAM_SELECT
PARAM_BOOLEAN
PARAM_FILE
IO_PARAM
IO_INPUT
IO_OUTPUT

Classes
-------
ToolsCategoryContainer
ToolIndexContainer
ToolContainer
ToolParameterContainer
ToolDatabaseContainer
CmdSelectContainer

"""


PARAM_NUMBER = "number"
PARAM_FLOAT = "float"
PARAM_INTEGER = "integer"
PARAM_STRING = "string"
PARAM_SELECT = "select"
PARAM_BOOLEAN = "boolean"
PARAM_FILE = "file"
IO_PARAM = "param"
IO_INPUT = "input"
IO_OUTPUT = "output"


class ToolsCategoryContainer:
    """Container for a category of tools

    These are the metadata of a tools category for the
    tool-shed structure

    id:
        ID of the category. It must be a unique name
    name:
        Name of the category. It is the name printed to the user interfaces
    thumbnail:
        URI to an image that illustrate the category tools
    parent:
        ID of the parent category in the category tree. Set to 'root' for a
        top level category

    """
    def __init__(self):
        self.id = ''
        self.name = ''
        self.thumbnail = ''
        self.doc = ''
        self.parent = 'root'


class ToolIndexContainer:
    """Container for a tool main information

    uri
        URI of the XML file
    id: str
        Id of the tool
    name: str
        Tool name
    version: str
        Tool version (ex 1.0.0)
    type
        Tool type ('sequential', 'merge')
    categories
        List of the tool categories

    """
    def __init__(self):
        self.uri = ''
        self.id = ''
        self.name = ''
        self.version = ''
        self.type = ''
        self.categories = []
        self.help = ''

    def to_dict(self):
        out = dict()
        out['uri'] = self.uri
        out['id'] = self.id
        out['name'] = self.name
        out['version'] = self.version
        out['type'] = self.type
        out['categories'] = self.categories
        out['help'] = self.help
        return out

    def serialize(self, direction: str = 'h', show_uri=False):
        """Serialize the tool main info

        Parameters
        ----------
        direction: str
            h for horizontal, and v for vertical
        show_uri: bool
            True to show the tool URI

        """
        type_ = 'sequential'
        if self.type != '':
            type_ = self.type

        if direction == 'h' and show_uri:
            return '{:>15}\t{:>15}\t{:>15}\t{:>15}\t{:>15}'.format(
                self.id + '_v' + self.version, self.name, self.version,
                type_, self.uri
            )
        elif direction == 'h' and not show_uri:
            return '{:>15}\t{:>15}\t{:>15}\t{:>15}'.format(
                self.id + '_v' + self.version, self.name, self.version,
                type_
            )

        sep = '\n'
        txt = (
            self.id
            + '_v'
            + self.version
            + sep
            + self.name
            + sep
            + self.version
            + sep
            + type_
            + sep
            + self.uri
        )
        for item in self.categories:
            txt += item + sep
        return txt


class CmdSelectContainer:
    """Container for a select parameter options

    Attributes
    ----------
    names: list
        List of the options names
    values: list
        List of the options values

    Methods
    -------
    size
        Number of options
    add
        Add an option

    """

    def __init__(self):
        self.names = []
        self.values = []

    def content_str(self):
        content = ""
        for i in range(len(self.values)):
            content += self.values[i] + ";"
        print("content_str", content)
        return content[:-1]

    def size(self):
        """Calculate the number of options

        Returns
        -------
        Int
            Number of options
        """
        return len(self.names)

    def add(self, name: str, value: str):
        """Add an option

        Parameters
        ----------
        name
            Name of the option
        value
            Value of the option
        """

        self.names.append(name)
        self.values.append(value)


class ToolTestParameterContainer:
    """Container for a tool test information

    Attributes
    ----------
    type: str
        Parameter type (param or output)
    name: str
        Name of the parameter
    value: str
        Value of the parameter
    file: str
        Reference file path for output
    compare: str
        Comparison method name

    """

    def __init__(self):
        self.type = ''  # param or output
        self.name = ''
        self.value = ''
        self.file = ''
        self.compare = ''

    def display(self):
        """Display the container content"""

        print("\ttype:", self.type)
        print("\tname:", self.name)
        print("\tvalue:", self.value)
        print("\tfile:", self.file)
        print("\tcompare:", self.compare)
        print("\t------------")


class ToolParameterContainer:
    """Container for a tool parameter information

    Attributes
    ---------
    name: str
        Parameter name
    description: str
        Parameter description
    value: str
        Parameter value
    type: str
        Parameter type (format)
    is_data: bool
        False if parameter is param and True if parameter is data
    io: str
        IO type if parameter is IO (in IO_XXX names)
    default_value: str
        Parameter default value
    select_info: BiCmdSelect
        Choices for a select parameter
    is_advanced: bool
        True if parameter is advanced

    """

    def __init__(self):
        self.name = ''  # str: parameter name
        self.description = ''  # str: Parameter description
        self.value = ''  # str: Parameter value
        self.type = ''  # str: parameter type (in PARAM_XXX names)
        self.is_data = False
        # bool: False if parameter is param and True if parameter is data
        self.io = ''  # str: IO type if parameter is IO (in IO_XXX names)
        self.default_value = ''  # str: Parameter default value
        self.select_info = (
            CmdSelectContainer()
        )  # BiCmdSelect: Choices for a select parameter
        self.is_advanced = False  # bool: True if parameter is advanced
        self.help = ''  # str: help text

    def display(self):
        """Display the tool parameter information to console"""

        print("\tname:", self.name)
        print("\tdescription:", self.description)
        print("\tvalue:", self.value)
        print("\ttype:", self.type)
        print("\tio:", self.io)
        print("\tdefault_value:", self.default_value)
        print("\tis_advanced:", self.is_advanced)
        print("\t------------")


class Tool:
    """Container for a tool parameter information

    Attributes
    ---------
    id: str
        Id of the tool
    name: str
        Tool name
    version: str
        Tool version (ex 1.0.0)
    description: str
        Tool short description (used for the man page)
    command: str
        Command executed when tool is ran
    inputs: list
        Tool inputs stored in a list of ToolParameter
    outputs: list
        Tool outputs stored in a list of ToolParameter
    tests: list
        List of unit tests
    help: str
        Url to the help page

    Methods
    -------
    is_param
        Check if a parameter exists
    inputs_size
        Returns the number of inputs
    outputs_size
        Returns the number of outputs
    display
        Display the tool information to console

    """
    def __init__(self):
        self.uri = ''
        self.id = ''
        self.name = ''
        self.version = ''
        self.description = ''
        self.requirements = list()
        self.command = ''
        self.inputs = []
        self.outputs = []
        self.help = ''
        self.categories = []
        self.tests = []
        self.type = 'sequential'

    def fullname(self):
        """fullname of the tool

        the full name is "{name}_v{version}"

        """
        return self.name + '_v' + self.version

    def is_param(self, name: str) -> bool:
        """Check if a parameter exists

        Parameters
        ----------
        name
            Name of the parameter to check

        Returns
        -------
        bool
            True if the parameter exists, False otherwise

        """

        for param in self.inputs:
            if param.name == name:
                return True
        for param in self.outputs:
            if param.name == name:
                return True
        return False

    def container(self):
        """Get the first container in the requirements

        Returns
        -------
        dict
            Description of the container requirement (origin, type, uri)

        """
        for req in self.requirements:
            if req['origin'] == 'container':
                return req
        return None

    def param_size(self):
        """Calculate the number of parameters

        Returns
        -------
        int
            Number of inputs

        """
        count = 0
        for param in self.inputs:
            if param.io == IO_PARAM:
                count += 1
        return count

    def inputs_size(self):
        """Calculate the number of inputs

        Returns
        -------
        int
            Number of inputs

        """
        return len(self.inputs)

    def outputs_size(self):
        """Calculate the number of outputs

        Returns
        -------
        int
            Number of outputs

        """
        return len(self.outputs)

    def display(self):
        """Print the tool information to console."""

        print('ToolInfo')
        print('-------------')
        print('xml file:', self.uri)
        print('id:', self.id)
        print('name:', self.name)
        print('version:', self.version)
        print('description:', self.description)
        print('help:', self.help)
        print('command:', self.command)
        print('inputs:')
        for param in self.inputs:
            param.display()
        print('outputs:')
        for param in self.outputs:
            param.display()
        print('tests:')
        for test in self.tests:
            test.display()
        print('requirements:')
        for req in self.requirements:
            print("origin:", req['origin'], "type", req['type'], "uri:",
                  req['uri'])

    def man(self):
        """Display the tool man page"""
        # 1. program name
        print(self.name, ':', self.description)
        # 2. list of args key, default, description
        for param in self.inputs:
            line_new = '\t{:>15}\t{:>15}\t{:>15}'.format(
                param.name, param.default_value, param.description
            )
            print(line_new)
        for param in self.outputs:
            line_new = '\t{:>15}\t{:>15}\t{:>15}'.format(
                param.name, param.default_value, param.description
            )
            print(line_new)
