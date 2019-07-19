# -*- coding: utf-8 -*-
"""BioImagePy process tools to run external processed.

This module contains a set of tools to run external processes 
(using the subprocess module) using a XML wrapper from the 
Galaxy project format. Data can be process using this module
either on directly on files or from python data. In the second
case, python data will be stored in temprary files for the process
execution.

Example
-------
This is a basic example of how to run a process on a file::

    >>> myprocess = BiProcess('/path/to/the/process.xml')
    >>> myprocess.exec('-input_tag', '/path/to/input/image.tif', 
    >>>            '-output_tag', '/path/to/output/image.tif'
    >>>            '-param1_tag', '2', 
    >>>            '-param2_', 2 ...) 

To process python data, you need to use the run method::    
    >>> myprocess = BiProcess('/path/to/the/process.xml')
    >>> myoutput = myprocess.run('-input_tag', '/path/to/input/image.tif',
    >>>            '-param1_tag', '2', 
    >>>            '-param2_', 2 ...) 


Notes
-----
    This module does not use the BioImageIT data file system. It can thus
    be used for any data processing purpose without taging the data in an
    BiExperimet data structure

Classes
-------
BiProcess
BiProcessParser
BiCmdSelect
BiProcessParameter
BiProcessInfo

Methods
-------
DATA_IMAGE
DATA_TXT
DATA_NUMBER
DATA_ARRAY
DATA_MATRIX
DATA_TABLE
PARAM_NUMBER
PARAM_STRING
PARAM_SELECT
PARAM_BOOLEAN
PARAM_HIDDEN
PARAM_FILE
IO_PARAM
IO_INPUT
IO_OUTPUT

Raises
------
BiProcessParseException
BiProcessExecException

"""

import os
import xml.etree.ElementTree as ET
from .core import BiObject
import subprocess
import tempfile 
from libtiff import TIFF
import imageio 
import shlex

def DATA_IMAGE():
    """Type for data image""" 

    return "image"

def DATA_TXT():
    """Type for data text""" 

    return "txt"   

def DATA_NUMBER():
    """Type for data number"""

    return "number"

def DATA_ARRAY(): 
    """Type for data array"""

    return "array"   

def DATA_MATRIX(): 
    """Type for data matrix"""

    return "matrix"     

def DATA_TABLE(): 
    """Type for data table"""

    return "table"

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

def PARAM_HIDDEN():
    """Type for parameter hidden""" 

    return "hidden"  

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


class BiProcessParseException(Exception):
   """Raised when an error occure during a process parsing"""

   pass

class BiProcessExecException(Exception):
   """Raised when an error occure during a process parsing"""

   pass   

class BiProcess(BiObject): 
    """Class that exec a process from a XML process file
    
    BiProcess class service is to execute a process described in 
    a XML file. The XML file must follow the BioImageIT XML format
    from the Galaxy Project format. To execute the process of file, use
    the exec() method, and to execute the process on python data, use 
    the run() method

    Parameters
    ----------
    xml_file_url
        Path of the XML process file

    Attributes
    ----------
    info 
        BiProcessInfo object that contains the process info extracted from the XML file

    """

    def __init__(self, xml_file_url : str):
        
        self._objectname = "BiProcess"
        self._xml_file_url = xml_file_url
        parser = BiProcessParser(xml_file_url)
        self.info = parser.parse()
        self.tmp_dir = tempfile.gettempdir()

    def display(self):
        """Display the process information in console"""

        self.info.display()    

    def man(self):
        """Display the process man page of the process. The man information are 
        collected from the XML file 
        
        """

        # 1. program name
        print(self.info.name, ':', self.info.description)
        # 2. list of args key, default, description
        for param in self.info.inputs:
            if param.type != PARAM_HIDDEN():
                line_new = '\t{:>15}\t{:>15}\t{:>15}'.format(param.name, param.default_value, param.description)
                print(line_new)
        for param in self.info.outputs:
            line_new = '\t{:>15}\t{:>15}\t{:>15}'.format(param.name, param.default_value, param.description)
            print(line_new)        

    def exec(self, *args):
        """Execute the process on files with the given arguments
        
        The inputs and outputs arguments have to be the path of the I/O data.
        args have to be pairs 'arg name, arg value' where arg name is the name
        of the parameter as given in the XML process file.

        Parameters
        ----------
        *args
            List of the parameters and I/O data given as pair 'arg name, arg value' 

        """

        # 1. check inputs
        for input_arg in self.info.inputs:
            if input_arg.name not in args and input_arg.type is not PARAM_HIDDEN():
                print('Warning (BiProcess): cannot find the input ' + input_arg.name + ' will use the default value: ' + input_arg.default_value)
                input_arg.value = input_arg.default_value

        for output_arg in self.info.outputs:
            if output_arg.name not in args:
                print('Warning (BiProcess): cannot find the input ' + output_arg.name + ' will use the default value: ' + output_arg.default_value)
                output_arg.value = output_arg.default_value
        
        # 2. exec    
        # 2.1- get the parameters values
        for i in range(len(args)):
            arg = args[i]
            for input_arg in self.info.inputs:
                if input_arg.name == arg and input_arg.type is not PARAM_HIDDEN():
                    input_arg.value = args[i+1]
            for output_arg in self.info.outputs:
                if output_arg.name == arg:    
                     output_arg.value = args[i+1] 

        # 2.2- build the command line 
        cmd = self.info.command   
        for input_arg in self.info.inputs:
            cmd = cmd.replace("${"+input_arg.name+"}", str(input_arg.value))
        for output_arg in self.info.outputs:
            cmd = cmd.replace("${"+output_arg.name+"}", str(output_arg.value))    

        cmd = " ".join(cmd.split())

        # 2.3. exec
        # try to find the program
        cmd_path = ''
        found_program = False
        if os.path.isfile(self.info.program):
            found_program = True
        else:
            xml_root_path = os.path.dirname(os.path.abspath(self._xml_file_url))
            if os.path.isfile( os.path.join(xml_root_path, self.info.program)):
                cmd_path = xml_root_path 
                found_program = True

        # run the program
        if not found_program:
            print("Warning: Cannot find a file corresponding to the program", self.info.program)   

        print("cmd:", os.path.join(cmd_path, cmd))
        args = shlex.split(os.path.join(cmd_path, cmd))
        subprocess.run(args)
        

    def exec_dir(self, *args):
        """Execute the process where inputs and outputs are directories
                
        The inputs and outputs arguments have to be the path list of the I/O data.
        args have to be pairs 'arg name, arg value' where arg name is the name
        of the parameter as given in the XML process file.

        Parameters
        ----------
        *args
            List of the parameters and I/O data given as pair 'arg name, arg value' 

        """    
        for input_arg in self.info.inputs:
            if input_arg.name not in args and input_arg.type is not PARAM_HIDDEN():
                print('Warning (BiProcess): cannot find the input ' + input_arg.name + ' will use the default value: ' + input_arg.default_value)
                input_arg.value = input_arg.default_value

        for output_arg in self.info.outputs:
            if output_arg.name not in args:
                print('Warning (BiProcess): cannot find the input ' + output_arg.name + ' will use the default value: ' + output_arg.default_value)
                output_arg.value = output_arg.default_value

                

    def exec_list(self, *args):
        """Execute the process where inputs and outputs are list of files"""    

    def run(self, *args):
        """Execute the process on python data with the given arguments
        
        The inputs and outputs data have to be stored in python data structures
        Depending on the I/O data type, the data will be stored in temporary data
        files to execute the processes and results will be loaded into python data
        structures and returned as dictionnary.

        Parameters
        ----------
        *args
            List of the parameters and I/O data given as pair 'arg name, arg value' 

        Returns
        -------
            the output if there is a single output (ex: image as numpy array)
            or a dictionnary of outputs if multiple outputs 
            (ex: {'-oimage': o_image, 'spots': spots})    

        """

        # 1. check inputs
        for input_arg in self.info.inputs:
            if input_arg.name not in args and input_arg.type != PARAM_HIDDEN():
                print('Warning (BiProcess): cannot find the input ' + input_arg.name + ' will use the default value: ' + input_arg.default_value)
                input_arg.value = input_arg.default_value

        # 2. exec    
        # 2.1. get the parameters values
        for i in range(len(args)):
            arg = args[i]
            for input_arg in self.info.inputs:
                if input_arg.name == arg and input_arg.type != PARAM_HIDDEN() and not input_arg.is_data:
                    input_arg.value = args[i+1]

        # 2.2. save the inputs into tmp files
        for i in range(len(args)):
            arg = args[i]
            for input_arg in self.info.inputs:
                if input_arg.name == arg and input_arg.type != PARAM_HIDDEN() and input_arg.is_data:
                    if input_arg.type == DATA_IMAGE():
                        image_tmp_path = os.path.join(self.tmp_dir, input_arg.name + ".tif")
                        tiff = TIFF.open(image_tmp_path, mode='w')
                        tiff.write_image(args[i+1])
                        tiff.close()
                        input_arg.value = image_tmp_path 
                    if input_arg.type == DATA_TXT():
                        # TODO save the data to file     
                        input_arg.value = os.path.join(self.tmp_dir, input_arg.name + ".txt") 

        # 2.3. create names for outputs files in tmp 
        for output_arg in self.info.outputs:     
            if output_arg.type == DATA_IMAGE():
                output_arg.value = os.path.join(self.tmp_dir, output_arg.name + ".tif") 
            elif output_arg.type == DATA_TXT():
                output_arg.value = os.path.join(self.tmp_dir, output_arg.name + ".txt")       

        # 2.4. build the command line   
        cmd = self.info.program + ' '
        for input_arg in self.info.inputs:
            cmd += input_arg.name + ' ' + str(input_arg.value) + ' '
        for output_arg in self.info.outputs:
            cmd += output_arg.name + ' ' + str(output_arg.value) + ' '    

        cmd = " ".join(cmd.split())

        # 2.4.2. replace the command variables
        xml_root_path = os.path.dirname(os.path.abspath(self._xml_file_url))
        cmd = cmd.replace("${pwd}", xml_root_path) 
        print('cmd: ', cmd)

        # 2.5. exec
        cmd_path = ''
        found_program = False
        if os.path.isfile(self.info.program):
            found_program = True

        
        if os.path.isfile( os.path.join(xml_root_path, self.info.program)):
           cmd_path = xml_root_path 
           found_program = True

        #print('run process: ', os.path.join(cmd_path, cmd))
        if found_program:
            subprocess.run(os.path.join(cmd_path, cmd).split())
        else:
            raise BiProcessExecException('Cannot find the program: ' + self.info.program)

        # 2.6. load and return the outputs
        if self.info.outputs_size() == 1:
            return imageio.imread(self.info.outputs[0].value)
            # return self.info.outputs[0].value 
        else:    
            return_data = {}
            for output_arg in self.info.outputs: 
                return_data[output_arg.name] = output_arg.value
            return return_data    

class BiProcessParser(BiObject):
    """Class that parse a process XML file and 
    
    The process information are parsed from the XML file and stored into 
    a BiProcessInfo structure 

    Parameters
    ----------
    xml_file_url
        Path of the XML process file

    Attributes
    ----------
    xml_file_url 
        Path of the XML process file

    Methodes
    --------
    parse
        Parse the XML file and returns the information into a BiProcessInfo    

    """

    def __init__(self, xml_file_url: str):
        self._objectname = "BiProcessParser"
        self.info = BiProcessInfo()
        self.xml_file_url = xml_file_url
        self.info.xml_file_url = xml_file_url

    def parse(self):    
        """Parse the XML file
        
        Returns
        -------
        BiProcessInfo
            The process information extracted from the XML file    
        
        """

        tree = ET.parse(self.xml_file_url)  
        self._root = tree.getroot()
        
        if self._root.tag != 'tool':
            raise BiProcessParseException('The process xml file must contains a <tool> root tag')

        self._parseTool()
        for child in self._root:
            if child.tag == 'description':
                desc = child.text
                desc = desc.replace('\t', '')
                self.info.description = desc
            elif child.tag == 'command':
                self._parse_command(child)
            elif child.tag == 'inputs':
                self._parse_inputs(child)        
            elif child.tag == 'outputs':
                self._parse_outputs(child)
            elif child.tag == 'help':
                self._parse_help(child)
            elif child.tag == 'categories':
                self._parse_categories(child)    

        self._parse_hidden_params()
        return self.info

    def _parseTool(self):
        """Parse the tool information"""

        if 'id' in self._root.attrib:
            self.info.id = self._root.attrib['id']
        if 'name' in self._root.attrib:
            self.info.name = self._root.attrib['name']
        if 'version' in self._root.attrib:
            self.info.version = self._root.attrib['version']  
        if 'type' in self._root.attrib:
            self.info.type = self._root.attrib['type']    

    def _parse_command(self, node):
        """Parse the tool command"""

        command = node.text
        command = command.replace('\t', '')
        command = command.replace('\n', '')
        self.info.command = command    
        self.info.command_args = command.split(' ')

    def _parse_help(self, node):
        """Parse the help information"""

        if 'url' in node.attrib:
            self.info.help = node.attrib['url']

    def _parse_categories(self, node):
        """Parse categories"""

        for child in node: 
            if child.tag == 'category':
                self.info.categories.append(child.text)

    def _parse_inputs(self, node):
        """Parse the inputs"""

        for child in node:  
            if child.tag == 'param':
                input_parameter = BiProcessParameter()
                input_parameter.io = IO_PARAM()
                input_parameter.is_data = False

                if 'name' in child.attrib:
                    input_parameter.name = child.attrib['name'] 

                if 'label' in child.attrib:
                    input_parameter.description = child.attrib['label'] 

                if 'type' in child.attrib:
                    if child.attrib['type'] == 'number':
                        input_parameter.type = PARAM_NUMBER()
                    elif child.attrib['type'] == 'string':
                        input_parameter.type = PARAM_STRING()
                    elif child.attrib['type'] == 'bool' or format == 'boolean':
                        input_parameter.type = PARAM_BOOLEAN()
                    else:
                        raise BiProcessParseException("The format of the input param " + input_parameter.name + " is not supported")

                if 'value' in child.attrib:
                    input_parameter.value = child.attrib['value'] 

                if 'advanced' in child.attrib:
                    if child.attrib['advanced'] == "True" or child.attrib['advanced'] == "true":
                        input_parameter.is_advanced = True
   
                if child.attrib['type'] == PARAM_SELECT():
                    # TODO: implement select case
                    input_parameter.selectInfo = BiCmdSelect()

                if 'default' in child.attrib:
                    input_parameter.default_value = child.attrib['default']  
                    input_parameter.value = child.attrib['default'] 
                input_parameter.value_suffix = '' 

                self.info.inputs.append(input_parameter)

            elif child.tag == 'data':   
                input_parameter = BiProcessParameter()
                input_parameter.io = IO_INPUT() 
                input_parameter.is_data = True

                if 'name' in child.attrib:
                    input_parameter.name = child.attrib['name'] 

                if 'label' in child.attrib:
                    input_parameter.description = child.attrib['label'] 
    
                if 'default' in child.attrib:
                    input_parameter.default_value = child.attrib['default'] 
                    input_parameter.value = child.attrib['default'] 

                if 'format' in child.attrib:
                    if child.attrib['format'] == 'image':
                        input_parameter.type = DATA_IMAGE()
                    elif child.attrib['format'] == 'txt':
                        input_parameter.type = DATA_TXT()  
                    elif child.attrib['format'] == 'array':
                        input_parameter.type = DATA_ARRAY()
                    elif child.attrib['format'] == 'matrix':
                        input_parameter.type = DATA_MATRIX()    
                    else:
                        raise BiProcessParseException("The format of the input data " + input_parameter.name + " is not supported")

                input_parameter.value_suffix = self._parse_parametervalue_suffix(input_parameter.name)
                self.info.inputs.append(input_parameter)   

    def _parse_parametervalue_suffix(self,parameter_name: str) -> str:
        """Parse the command line to search if a input data have a suffix (ex: $(data)_suffix)"""

        suffix = ''
        search = '${'+parameter_name+'}'
        for arg in self.info.command_args:
            if arg.startswith(search):
                suffix = arg.replace(search, '')
                return suffix
        return suffix

    def _parse_outputs(self, node):   
        """Parse the outputs."""

        for child in node:  
            if child.tag == 'data':
                output_parameter = BiProcessParameter()
                output_parameter.io = IO_OUTPUT()
                output_parameter.is_data = True

                if 'name' in child.attrib:
                    output_parameter.name = child.attrib['name'] 

                if 'label' in child.attrib:
                    output_parameter.description = child.attrib['label'] 
    
                if 'default' in child.attrib:
                    output_parameter.default_value = child.attrib['default'] 
                    output_parameter.value = child.attrib['default'] 

                if 'format' in child.attrib:
                    if child.attrib['format'] == 'image':
                        output_parameter.type = DATA_IMAGE()
                    elif child.attrib['format'] == 'txt':  
                        output_parameter.type = DATA_TXT()  
                    elif child.attrib['format'] == 'number': 
                        output_parameter.type = DATA_NUMBER()      
                    elif child.attrib['format'] == 'array': 
                        output_parameter.type = DATA_ARRAY()   
                    elif child.attrib['format'] == 'matrix': 
                        output_parameter.type = DATA_MATRIX()  
                    elif child.attrib['format'] == 'table': 
                        output_parameter.type = DATA_TABLE()           
                    else:
                        raise BiProcessParseException("The format of the output data " + output_parameter.name + " is not supported")
                
                output_parameter.value_suffix = self._parse_parametervalue_suffix(output_parameter.name)
                self.info.outputs.append(output_parameter) 

    def _parse_hidden_params(self):
        """Parse the hidden parameters.
        
        Hidden parameters state for the parameters in the command line that are 
        not accessible by the user
        
        """

        # Parse the program name
        if len(self.info.command_args) > 0:
            self.info.program = self.info.command_args[0]
        else:
            raise BiProcessParseException("Cannot parse the command line")  

        # Parse hidden parameters
        for arg in self.info.command_args:
            if not arg.startswith('${') and not self.info.is_param(arg) and arg != self.info.program:
                param = BiProcessParameter()
                param.name = arg
                param.type = PARAM_HIDDEN()
                self.info.inputs.append(param)

class BiCmdSelect(BiObject):
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


class BiProcessParameter(BiObject):
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
        self.selectInfo = BiCmdSelect() # BiCmdSelect: Choices for a select parameter
        self.value_suffix = '' # str: Parameter suffix (needed if programm add suffix to IO)
        self.is_advanced = False # bool: True if parameter is advanced

    def display(self):
        """Display the process parameter informations to console"""

        print("\tname:", self.name) 
        print("\tdescription:", self.description)  
        print("\tvalue:", self.value)  
        print("\ttype:", self.type)
        print("\tio:", self.io) 
        print("\tdefault_value:", self.default_value) 
        print("\tvalue_suffix:", self.value_suffix)
        print("\tis_advanced:", self.is_advanced)
        print("\t------------")


class BiProcessInfo(BiObject):
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
        Process inputs stored in a list of BiProcessParameter
    outputs: list
        Process outputs stored in a list of BiProcessParameter
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

        self.xml_file_url = ''
        self.id = ''
        self.name = ''
        self.version = ''
        self.description = ''
        self.command = ''
        self.command_args = []
        self.program = ''
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

        print('BiProcessInfo')
        print('-------------')
        print('xml file:', self.xml_file_url)  
        print('id:', self.id)  
        print('name:', self.name) 
        print('version:', self.version) 
        print('description:', self.description) 
        print('help:', self.help) 
        print('program:', self.program) 
        print('command:', self.command) 
        print('args:', self.command) 
        print('inputs:')
        for param in self.inputs:
            param.display()
        for param in self.outputs:
            param.display()    
