# -*- coding: utf-8 -*-
"""BioImagePy local process service.

This module implements the local service for process
(Process class) execution. 

Classes
------- 
ProcessServiceProvider

"""
import os
import xml.etree.ElementTree as ET
import json
import yaml

from bioimagepy.processes.containers import (ProcessContainer, ProcessIndexContainer, 
                                             ProcessParameterContainer, CmdSelectContainer, 
                                             IO_INPUT, PARAM_NUMBER,
                                             PARAM_STRING, PARAM_SELECT, PARAM_BOOLEAN, PARAM_FILE,
                                             IO_PARAM, IO_INPUT, IO_OUTPUT,
                                             ProcessCategoryContainer)
from bioimagepy.processes.exceptions import ProcessServiceError

class LocalProcessServiceBuilder:
    """Service builder for the process service"""
    def __init__(self):
        self._instance = None

    def __call__(self, xml_dirs, categories, **_ignored):
        if not self._instance:
            self._instance = LocalProcessService()
            print('xml dirs:', xml_dirs)
            self._instance.xml_dirs = xml_dirs
            self._instance.categories_json = categories
            self._instance._load()
        return self._instance

class LocalProcessService:
    """Service for local process
    
    To initialize the database, you need to set the xml_dirs from 
    the configuration and then call initialize
    
    """
    def __init__(self):
        self.service_name = 'LocalProcessService'
        self.xml_dirs = []
        self.categories_json = ''
        self.database = {}
        self.categories = []

    def _load_categories(self):
        """Load the categories database

        parse the categories json file and store it in a list 
        of categories containers

        """    
        self.categories = []
        # read json
        if os.path.getsize(self.categories_json) > 0:
            with open(self.categories_json) as json_file:  
                categories_dict = json.load(json_file)

        categories_json_dirname = os.path.dirname(self.categories_json)
        for categories in categories_dict['categories']:
            container = ProcessCategoryContainer()
            container.id = categories['id']
            container.name = categories['name']
            container.thumbnail = os.path.join(categories_json_dirname, categories['thumbnail'])
            container.parent = categories['parent']
            self.categories.append(container)
    
    def _load(self):
        """Build the process and categories database"""
        self._load_datbase()
        self._load_categories()

    def _load_datbase(self):
        """Build the database

        Parse the source directories and build the database
    
        """
        for dir in self.xml_dirs:
            #print("process database parse dir ", dir)
            #print("process database parse dir abs ", os.path.abspath(dir))
            self._parse_dir(os.path.abspath(dir))
    
    def _parse_dir(self, rootdir:str):
        """Load process info XMLs

        Parameters
        ----------
        rootdir
            Directory to parse

        """
        for currentpath, subs, files in os.walk(rootdir):
            for file in files:
                if file.endswith('.xml'):
                    process_path = os.path.join(currentpath, file)
                    #print("parse file:", process_path)
                    parser = ProcessParser(process_path)
                    info = parser.parse_main_info()
                    if info:
                        self.database[info.id + '_v' + info.version] = info    

    def read_process(self, uri: str) -> ProcessContainer:
        """Read a process from its URI
        
        Parameters
        ----------
        uri
            URI of the process

        Returns
        -------
        A container of the process metadata    
        
        """  
        parser = ProcessParser(uri)
        return parser.parse()

    def read_process_index(self, uri:str) -> ProcessIndexContainer:
        """Read the basic indexation information of a Process
        
        Parameters
        ----------
        uri
            URI of the process

        Returns
        -------
        process index information    
        
        """    
        parser = ProcessParser(uri)
        return parser.parse_main_info()

    def search(self, keyword:str):
        """Search a process using a keyword in the database
        
        This method print the list of funded processed

        Parameters
        ----------
        keyword
            Keyword to search in the database 

        Returns
        -------
        The list of the processes index information     
        
        """
        list = []
        if keyword == '':
            for name in self.database:
                list.append(self.database[name])
        else:    
            for name in self.database:
                if keyword.lower() in name.lower():
                    list.append(self.database[name])
        return list  

    def get_process(self, fullname:str) -> str:
        """Get a process by name
        
        Parameters
        ----------
        fullname
            Fullname of the process ({name}_v{version})
        
        Returns
        -------
        The URI of the process

        """  
        if fullname in self.database:
            return self.database[fullname].uri
        return None      

    def get_categories(self, parent:str) -> list:
        """Get a list of categories for a given parent  

        parent
            ID of the parent category

        """   
        outlist = []
        for category in self.categories:
            if category.parent == parent:
                outlist.append(category)
        return outlist     

    def get_category_processes(self, category:str) -> list:
        """Get the list of processes with the given category

        category
            ID of the category

        """    
        outlist = []
        for name in self.database:
            process_container = self.database[name]
            if category in process_container.categories:
                outlist.append(process_container)    
        return outlist  

    def get_processes_database(self):
        """Get the dictionary of processed"""
        return self.database          


class ProcessParser():
    """Parse a process XML file 
    
    The process information are parsed from the XML file and stored into 
    a ProcessInfo structure 

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
        Parse the XML file and returns the information into a ProcessInfo    

    """
    def __init__(self, xml_file_url: str):
        self.info = ProcessContainer()
        self.xml_file_url = xml_file_url
        self.info.uri = xml_file_url

    def parse_main_info(self) -> ProcessIndexContainer:
        """Parse the name of the process
        
        Returns
        -------
        The name of the process

        """
        tree = ET.parse(self.xml_file_url)  
        self._root = tree.getroot()

        if self._root.tag != 'tool':
            return None

        info = ProcessIndexContainer()
        info.uri = self.xml_file_url
        if 'id' in self._root.attrib:
            info.id = self._root.attrib['id']
        if 'name' in self._root.attrib:
            info.name = self._root.attrib['name']
        if 'version' in self._root.attrib:
            info.version = self._root.attrib['version']  
        if 'type' in self._root.attrib:
            info.type = self._root.attrib['type']  
        for child in self._root:
            if child.tag == 'help':
                tmp = child.text 
                tmp = tmp.replace(" ", "")
                tmp = tmp.replace("\n", "")
                tmp = tmp.replace("\t", "")
                info.help = tmp
                break  
        info.categories = self._parse_categories()
        return info        


    def parse(self) -> ProcessContainer:    
        """Parse the XML file
        
        Returns
        -------
        The process information extracted from the XML file    
        
        """
        tree = ET.parse(self.xml_file_url)  
        self._root = tree.getroot()
        
        if self._root.tag != 'tool':
            raise ProcessServiceError('The process xml file must contains a <tool> root tag')

        self._parseTool()
        for child in self._root:
            if child.tag == 'description':
                desc = child.text
                desc = desc.replace('\t', '')
                self.info.description = desc
            elif child.tag == 'requirements':
                self._parse_requirements(child)    
            elif child.tag == 'command':
                self._parse_command(child)
            elif child.tag == 'inputs':
                self._parse_inputs(child)        
            elif child.tag == 'outputs':
                self._parse_outputs(child)
            elif child.tag == 'help':
                self._parse_help(child)   
        self.info.categories = self._parse_categories()
        return self.info

    def _parse_requirements(self, node):
        """Parse the requirements"""

        for child in node: 
            requirement = dict()
            if child.tag == 'container':
                requirement['origin'] = 'container'
                if 'type' in child.attrib:
                    requirement['type'] = child.attrib['type'] 
                requirement['uri'] = child.text

            self.info.requirements.append(requirement)

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

    def _parse_help(self, node):
        """Parse the help information"""
        tmp = node.text
        tmp = tmp.replace(" ", "")
        tmp = tmp.replace("\n", "")
        tmp = tmp.replace("\t", "")
        self.info.help = tmp

    def _parse_inputs(self, node):
        """Parse the inputs"""

        for child in node:  
            if child.tag == 'param':
                input_parameter = ProcessParameterContainer()

                if 'name' in child.attrib:
                    input_parameter.name = child.attrib['name'] 

                if 'argument' in child.attrib:
                    input_parameter.name = child.attrib['argument'].replace("-", "")  

                if 'label' in child.attrib:
                    input_parameter.description = child.attrib['label'] 

                if 'help' in child.attrib:
                    input_parameter.help = child.attrib['help']   

                if 'optional' in child.attrib:
                    if child.attrib['optional'] == "true" or child.attrib['optional'] == "True":
                        input_parameter.is_advanced = True
                    else:
                        input_parameter.is_advanced = False 

                if 'value' in child.attrib:
                    input_parameter.default_value = child.attrib['value'] 
                    input_parameter.value = child.attrib['value']                  

                if 'type' in child.attrib:
                    if child.attrib['type'] == 'data':
                        input_parameter.io = IO_INPUT() 
                        input_parameter.is_data = True
    
                        if 'format' in child.attrib:
                            input_parameter.type = child.attrib['format']
                    else:
                        input_parameter.io = IO_PARAM()
                        input_parameter.is_data = False
                         
                        if child.attrib['type'] == 'number' or child.attrib['type'] == 'float' or child.attrib['type'] == 'integer':
                            input_parameter.type = PARAM_NUMBER()
                        elif child.attrib['type'] == 'string' or child.attrib['type'] == 'text':
                            input_parameter.type = PARAM_STRING()
                        elif child.attrib['type'] == 'bool' or child.attrib['type'] == 'boolean':
                            input_parameter.type = PARAM_BOOLEAN()
                        elif child.attrib['type'] == PARAM_SELECT():
                            input_parameter.type = PARAM_SELECT()
                            input_parameter.select_info = CmdSelectContainer()
                            #print("select parse option:")
                            for optionnode in child:  
                                if optionnode.tag == 'option':
                                    input_parameter.select_info.add(optionnode.text, optionnode.attrib['value'])
                        else:
                            raise ProcessServiceError("The format of the input param " + input_parameter.name + " is not supported")

                self.info.inputs.append(input_parameter)


    def _parse_outputs(self, node):   
        """Parse the outputs."""

        for child in node:  
            if child.tag == 'data':
                output_parameter = ProcessParameterContainer()
                output_parameter.io = IO_OUTPUT()
                output_parameter.is_data = True

                if 'name' in child.attrib:
                    output_parameter.name = child.attrib['name'] 

                if 'label' in child.attrib:
                    output_parameter.description = child.attrib['label'] 

                if 'format' in child.attrib:
                    output_parameter.type = child.attrib['format']
                    
                self.info.outputs.append(output_parameter)   

    def _parse_categories(self):
        """Parse categories from the .shed.yml file"""
        # get the yml file
        shed_file = os.path.join(os.path.dirname(self.xml_file_url), '.shed.yml')
        if not os.path.isfile(shed_file):
            return []

        with open(shed_file) as file:
            shed_file_content = yaml.load(file, Loader=yaml.FullLoader) 
 
        return shed_file_content["categories"]  
