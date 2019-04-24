import os
import xml.etree.ElementTree as ET

def TYPE_IMAGE():
    return "image"

def TYPE_NUMBER():
    return "number"

def TYPE_STRING():
    return "string"

def TYPE_SELECT():
    return "select"

def TYPE_BOOLEAN():
    return "boolean"

def TYPE_HIDDEN():
    return "hidden"    

def IO_INPUT():
    return "input" 

def IO_OUTPUT():
    return "output"     


class BiProcessParseException(Exception):
   """Raised when an error occure during a process parsing"""
   pass

class BiProcess(): 
    """Abstract class that store a process information"""
    def __init__(self, xml_file_url : str):
        self._objectname = "BiProcess"
        self.info = BiProcessInfo()
        self.xml_file_url = xml_file_url
        self._parse()

    def _parse(self):    
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
                self._parseCommand(child)
            elif child.tag == 'inputs':
                self._parseInputs(child)        
            elif child.tag == 'outputs':
                self._parseOutputs(child)
            elif child.tag == 'help':
                self._parseHelp(child)

            #print(child.tag, child.attrib)

    def _parseTool(self):
        """Parse the tool information"""
        if 'id' in self._root.attrib:
            self.info.id = self._root.attrib['id']
        if 'name' in self._root.attrib:
            self.info.name = self._root.attrib['name']
        if 'version' in self._root.attrib:
            self.info.version = self._root.attrib['version']  

    def _parseCommand(self, node):
        """Parse the tool command"""
        command = node.text
        command = command.replace('\t', '')
        command = command.replace('\n', '')
        self.info.command = command    

    def _parseHelp(self, node):
        if 'url' in node.attrib:
            self.info.help = node.attrib['url']

    def _parseInputs(self, node):
        print("parse input not implemented") 
        for child in node:  
            if child.tag == 'param':

                input_parameter = BiProcessParameter()
                if 'name' in child.attrib:
                    input_parameter.name = child.attrib['name'] 
                if 'label' in child.attrib:
                    input_parameter.description = child.attrib['label'] 
                if 'type' in child.attrib:
                    input_parameter.type = child.attrib['type'] 
                if ( child.attrib['type'] == TYPE_SELECT ):
                    # TODO: implement select case
                    input_parameter.selectInfo = BiCmdSelect()
                input_parameter.io = IO_INPUT() 
                input_parameter.defaultValue= child.attrib['default']  
                input_parameter.valueSuffix = '' 
                input_parameter.isAdvanced = False 
                self.info.inputs.append(input_parameter)

            elif child.tag == 'data':   
                print("found input data ", child.attrib['name'])    

    def _parseOutputs(self, node):    
        print("parse output not implemented")    

    def display(self):
        self.info.display()    


class BiCmdSelect():
    """Contains a select parameter options"""
    def __init__(self):
        self.names = []
        self.values = []

    def size(self):
        return len(self.names)    

    def add(self, name: str, value: str):
        self.names.append(name)
        self.values.append(value)    


class BiProcessParameter():
    """Contains a parameter information"""
    def __init__(self):
        self.name = '' # str: parameter name
        self.description = '' # str: Parameter description
        self.value = '' # str: Parameter value
        self.type = '' # str: parameter type (in TYPE_XXX names)
        self.io = '' # str: IO type if parameter is IO (in IO_XXX names)
        self.defaultValue= '' # str: Parameter default value
        self.selectInfo = BiCmdSelect() # BiCmdSelect: Choices for a select parameter
        self.valueSuffix = '' # str: Parameter suffix (needed if programm add suffix to IO)
        self.isAdvanced = False # bool: True if parameter is advanced


class BiProcessInfo:
    def __init__(self):
        self.id = ''
        self.name = ''
        self.version = ''
        self.description = ''
        self.command = ''
        self.inputs = []
        self.outputs = []
        self.help = ''

    def inputs_size(self):
        return len(self.inputs)

    def output_size(self):
        return len(self.outputs)  

    def display(self):
        print('BiProcessInfo')
        print('-------------')
        print('id:', self.id)  
        print('name:', self.name) 
        print('version:', self.version) 
        print('description:', self.description) 
        print('help:', self.help) 


 