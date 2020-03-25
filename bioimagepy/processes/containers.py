# -*- coding: utf-8 -*-
"""BioImagePy process containers.

This module contains containers for Process info
and process database

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
ProcessIndexContainer
ProcessContainer
ProcessParameterContainer
ProcessDatabaseContainer
CmdSelectContainer

"""

def PARAM_NUMBER():
    """Type for parameter number""" 

    return "number"

def PARAM_STRING():
    """Type for parameter string""" 

    return "string"

def PARAM_SELECT():
    """Type for parameter select""" 

    return "select"

def PARAM_BOOLEAN():
    """Type for parameter boolean""" 

    return "boolean" 

def PARAM_FILE():
    """Type for parameter hidden""" 

    return "file"  

def IO_PARAM():
    """I/O for parameter""" 

    return "param" 

def IO_INPUT():
    """I/O for data input"""

    return "input" 

def IO_OUTPUT():
    """I/O for data output"""

    return "output" 

class ProcessIndexContainer():
    """Container for a process main information

    uri
        URI of the XML file
    id: str
        Id of the process
    name: str
        Process name
    version: str
        Process version (ex 1.0.0)
    type
        Process type ('sequential', 'merge')    

    """
    def __init__(self):
        self.uri = ''
        self.id = ''
        self.name = ''
        self.version = ''
        self.type = ''

    def serialize(self, direction:str='h'):
        """Serialize the process main info
        
        Parameters
        ----------
        direction
            h for horizontal, and v for vertical
        
        """

        type = 'sequential'
        if self.type != '':
            type = self.type

        if direction == 'h':
            return '{:>15}\t{:>15}\t{:>15}\t{:>15}\t{:>15}'.format(self.id + '_v' + self.version, self.name, self.version, type, self.uri)

        sep = '\n'    
        return self.id + '_v' + self.version + sep + self.name + sep + self.version + sep + type + sep + self.uri    


class CmdSelectContainer():
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
        print("contentstr", content)    
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
        
        Parameters:
        name
            Name of the option
        value
            Value of the option    
        """

        self.names.append(name)
        self.values.append(value)  

class ProcessParameterContainer():
    """Container for a process parameter information

    Attributs
    ---------
    name: str
        Parameter name
    desscription: str
        Parameter description  
    value: str
        Parameter value
    type: str 
        Parameter type (in PARAM_XXX names)
    is_data: bool
        False if parameter is param and True if parameter is data
    io: str 
        IO type if parameter is IO (in IO_XXX names)
    default_value: str
        Parameter default value
    selectInfo: BiCmdSelect
        Choices for a select parameter
    value_suffix: str
        Parameter suffix (needed if programm add suffix to IO)
    is_advanced: bool
        True if parameter is advanced    
    
    """
    def __init__(self):
        self.name = '' # str: parameter name
        self.description = '' # str: Parameter description
        self.value = '' # str: Parameter value
        self.type = '' # str: parameter type (in PARAM_XXX names)
        self.is_data = False # bool: False if parameter is param and True if parameter is data
        self.io = '' # str: IO type if parameter is IO (in IO_XXX names)
        self.default_value = '' # str: Parameter default value
        self.select_info = CmdSelectContainer() # BiCmdSelect: Choices for a select parameter
        self.is_advanced = False # bool: True if parameter is advanced
        self.help = '' # str: help text

    def display(self):
        """Display the process parameter informations to console"""

        print("\tname:", self.name) 
        print("\tdescription:", self.description)  
        print("\tvalue:", self.value)  
        print("\ttype:", self.type)
        print("\tio:", self.io) 
        print("\tdefault_value:", self.default_value) 
        print("\tis_advanced:", self.is_advanced)
        print("\t------------")


class ProcessContainer():
    """Container for a process parameter information
        
    Attributs
    ---------
    id: str
        Id of the process
    name: str
        Process name
    version: str
        Process version (ex 1.0.0)
    description: str
        Process short description (used for the man page)
    command: str
        Command executed when process is ran
    command_args: list
        List of arguments obtained by parsing the command
    program: str
        Name (or path) of the program obtained by parsing the command
    inputs: list
        Process inputs stored in a list of ProcessParameter
    outputs: list
        Process outputs stored in a list of ProcessParameter
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
        Display the process informations to console    
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
        self.type = 'sequential'

    def is_param(self, name: str) -> bool:
        """Check if a parameter exists
        
        Parameters
        ----------
        name
            Name of the parameter to check

        Returns
        -------
        bool
            True if the parameter exists, False otherwhise    
        
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
            Desctiption of the container requirement (origin, type, uri)
        
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
            if param.io == IO_PARAM():
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
        """Print the process information to console."""

        print('ProcessInfo')
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
        print('requirements:')
        for req in self.requirements:
            print("origin:",req['origin'], "type", req['type'], "uri:",req['uri'])