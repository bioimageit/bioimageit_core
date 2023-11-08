# -*- coding: utf-8 -*-
"""BioImagePy local process service.

This module implements the local service for process
(Process class) execution. 

Classes
------- 
ProcessServiceProvider

"""
import os
import xml.etree.ElementTree as ETree
import json
import yaml

from bioimageit_core.containers.pipeline_containers import (Pipeline, PipelineParameter, 
                                                            PipelineStep, PipelineInput, 
                                                            PipelineOutput)
from bioimageit_core.containers.tools_containers import (Tool,
                                                         ToolIndexContainer,
                                                         ToolParameterContainer,
                                                         CmdSelectContainer,
                                                         ToolTestParameterContainer,
                                                         ToolsCategoryContainer,
                                                         IO_INPUT,
                                                         IO_OUTPUT,
                                                         IO_PARAM,
                                                         PARAM_NUMBER,
                                                         PARAM_FLOAT,
                                                         PARAM_INTEGER,
                                                         PARAM_SELECT,
                                                         PARAM_BOOLEAN,
                                                         PARAM_STRING
                                                         )
from bioimageit_core.core.exceptions import ToolsServiceError, ToolNotFoundError


class LocalToolsServiceBuilder:
    """Service builder for the process service"""

    def __init__(self):
        self._instance = None

    def __call__(self, xml_dirs, categories, **_ignored):
        if not self._instance:
            self._instance = LocalToolsService()
            self._instance.xml_dirs = xml_dirs
            self._instance.categories_json = categories
            self._instance.load()
        return self._instance


class LocalToolsService:
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

        categories_json_dir_name = os.path.dirname(self.categories_json)
        for categories in categories_dict['categories']:
            container = ToolsCategoryContainer()
            container.id = categories['id']
            container.name = categories['name']
            if 'doc' in categories:
                container.doc = categories['doc']
            container.thumbnail = os.path.join(
                categories_json_dir_name, categories['thumbnail']
            )
            container.parent = categories['parent']
            self.categories.append(container)

    def load(self):
        """Build the process and categories database"""
        self._load_database()
        self._load_categories()

    def _load_database(self):
        """Build the database

        Parse the source directories and build the database

        """
        for dir_ in self.xml_dirs:
            # print("process database parse dir ", dir_)
            # print("process database parse dir abs ", os.path.abspath(dir_))
            self._parse_dir(os.path.abspath(dir_))

    def _parse_dir(self, root_dir: str):
        """Load process info XMLs

        Parameters
        ----------
        root_dir
            Directory to parse

        """
        for current_path, subs, files in os.walk(root_dir):
            for file in files:
                if file.endswith('.xml'):
                    process_path = os.path.join(current_path, file)
                    parser = ToolParser(process_path)
                    info = parser.parse_main_info()
                    if info:
                        self.database[info.id + '_v' + info.version] = info

    @staticmethod
    def read_tool(uri: str) -> Tool:
        """Read a tool from its URI

        Parameters
        ----------
        uri
            URI of the tool

        Returns
        -------
        A container of the tool metadata

        """
        parser = ToolParser(uri)
        return parser.parse()

    @staticmethod
    def read_process_index(uri: str) -> ToolIndexContainer:
        """Read the basic indexation information of a Process

        Parameters
        ----------
        uri
            URI of the process

        Returns
        -------
        process index information

        """
        parser = ToolParser(uri)
        return parser.parse_main_info()

    def search(self, keyword: str):
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
        list_ = []
        if keyword == '':
            for name in self.database:
                list_.append(self.database[name])
        else:
            for name in self.database:
                if keyword.lower() in name.lower():
                    list_.append(self.database[name])
        return list_

    def get_tool(self, fullname: str):
        """Get a process by name

        Parameters
        ----------
        fullname
            Fullname of the process ({name}_v{version})

        Returns
        -------
        The URI of the process or None

        """
        print('get tool:', fullname)
        if fullname in self.database:
            parser = ToolParser(self.database[fullname].uri)
            return parser.parse()
        else:
            raise ToolNotFoundError(f'The tool {fullname} cannot be found in the database')

    def get_categories(self, parent: str) -> list:
        """Get a list of categories for a given parent

        parent
            ID of the parent category

        """
        out_list = []
        for category in self.categories:
            if category.parent == parent:
                out_list.append(category)
        return out_list

    def get_category_tools(self, category: str) -> list:
        """Get the list of tools with the given category

        category
            ID of the category

        """
        out_list = []
        for name in self.database:
            process_container = self.database[name]
            if category in process_container.categories:
                out_list.append(process_container)
        return out_list

    def get_processes_database(self):
        """Get the dictionary of processed"""
        return self.database

    def get_pipeline(self, md_uri):
        """Read a pipeline from storage

        Parameters
        ----------
        md_uri: str
            URI of the pipeline file

        Returns
        -------
        instance of Pipeline     
        """
        parser = PipelineParser(md_uri)
        return parser.parse()


class PipelineParser:
    def __init__(self, pipeline_file):
        self.pipeline_file = pipeline_file
        self.pipeline = None

    def parse(self):
        self.pipeline = Pipeline()

        json_data = None 
        if os.path.getsize(self.pipeline_file) > 0:
            with open(self.pipeline_file) as json_file:
                json_data = json.load(json_file)

        self.pipeline.name = json_data['name']
        self.pipeline.description = json_data['description']
        self.pipeline.user = json_data['user']
        self.pipeline.date = json_data['date']
        self.pipeline.uuid = json_data['uuid']
        self.pipeline.bioimageit_version = json_data['bioimageit_version']
        for step in json_data['steps']:
            step_container = PipelineStep()
            step_container.name = step['name']
            step_container.tool = step['tool']
            step_container.output_dataset_name = step['output_dataset_name']
            for input in step['inputs']:
                input_container = PipelineInput()
                input_container.name = input['name']
                input_container.dataset = input['dataset']
                input_container.query = input['query']
                input_container.origin_output_name = input['origin_output_name']
                step_container.inputs.append(input_container)
            for parameter in step['parameters']:   
                prameter_container = PipelineParameter(parameter['name'], parameter['value'])
                step_container.parameters.append(prameter_container)
            for output in step['outputs']:
                output_container = PipelineOutput(output['name'], output['save'])    
                step_container.outputs.append(output_container)
            self.pipeline.steps.append(step_container)   
        return self.pipeline    


class ToolParser:
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

    Methods
    --------
    parse
        Parse the XML file and returns the information into a ProcessInfo

    """

    def __init__(self, xml_file_url: str):
        self.info = Tool()
        self.xml_file_url = xml_file_url
        self.info.uri = xml_file_url
        self._root = None

    def parse_main_info(self):
        """Parse the name of the process

        Returns
        -------
        The the process container (ProcessIndexContainer) or None

        """
        # print('parse xml file:', self.xml_file_url)
        try:
            tree = ETree.parse(self.xml_file_url)
        except ETree.ParseError as e:
            raise ToolsServiceError(str(e))

        self._root = tree.getroot()

        if self._root.tag != 'tool':
            return None

        info = ToolIndexContainer()
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

    def parse(self) -> Tool:
        """Parse the XML file

        Returns
        -------
        The process information extracted from the XML file

        """
        try:
            tree = ETree.parse(self.xml_file_url)
        except ETree.ParseError as e:
            raise ToolsServiceError(str(e))   
            
        self._root = tree.getroot()

        if self._root.tag != 'tool':
            raise ToolsServiceError(
                'The process xml file must contains a <tool> root tag'
            )

        self._parse_tool()
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
            elif child.tag == 'tests':
                self._parse_tests(child)
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
            elif child.tag == 'package':
                requirement['origin'] = 'package'
                if 'type' in child.attrib:
                    requirement['type'] = child.attrib['type']
                else:
                    requirement['type'] = ''
                if 'env' in child.attrib:
                    requirement['env'] = child.attrib['env']
                else:
                    requirement['env'] = ''    
                if 'init' in child.attrib:
                    requirement['init'] = child.attrib['init']
                else:
                    requirement['init'] = ''
                requirement['package'] = child.text

            self.info.requirements.append(requirement)

    def _parse_tool(self):
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
        command = command.replace('$__tool_directory__',
                                  os.path.dirname(self.xml_file_url) + os.sep)
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
                input_parameter = ToolParameterContainer()

                if 'name' in child.attrib:
                    input_parameter.name = child.attrib['name']

                if 'argument' in child.attrib:
                    input_parameter.name = child.attrib['argument'].\
                        replace("-", "")

                if 'label' in child.attrib:
                    input_parameter.description = child.attrib['label']

                if 'help' in child.attrib:
                    input_parameter.help = child.attrib['help']

                if 'optional' in child.attrib:
                    if (
                        child.attrib['optional'] == "true"
                        or child.attrib['optional'] == "True"
                    ):
                        input_parameter.is_advanced = True
                    else:
                        input_parameter.is_advanced = False

                if 'value' in child.attrib:
                    input_parameter.default_value = child.attrib['value']
                    input_parameter.value = child.attrib['value']

                if 'type' in child.attrib:
                    if child.attrib['type'] == 'data':
                        input_parameter.io = IO_INPUT
                        input_parameter.is_data = True

                        if 'format' in child.attrib:
                            input_parameter.type = child.attrib['format']
                    else:
                        input_parameter.io = IO_PARAM
                        input_parameter.is_data = False

                        if child.attrib['type'] == 'number':
                            input_parameter.type = PARAM_NUMBER
                        elif child.attrib['type'] == 'float':
                            input_parameter.type = PARAM_FLOAT
                        elif child.attrib['type'] == 'integer':
                            input_parameter.type = PARAM_INTEGER
                        elif child.attrib['type'] == 'string' or child.attrib['type'] == 'text':
                            input_parameter.type = PARAM_STRING
                        elif child.attrib['type'] == 'bool' or child.attrib['type'] == 'boolean':
                            input_parameter.type = PARAM_BOOLEAN
                        elif child.attrib['type'] == PARAM_SELECT:
                            input_parameter.type = PARAM_SELECT
                            input_parameter.select_info = CmdSelectContainer()
                            # print("select parse option:")
                            for option_node in child:
                                if option_node.tag == 'option':
                                    input_parameter.select_info.add(
                                        option_node.text,
                                        option_node.attrib['value']
                                    )
                        else:
                            raise ToolsServiceError(
                                "The format of the input param "
                                + input_parameter.name
                                + " is not supported"
                            )
                self.info.inputs.append(input_parameter)

    def _parse_outputs(self, node):
        """Parse the outputs."""

        for child in node:
            if child.tag == 'data':
                output_parameter = ToolParameterContainer()
                output_parameter.io = IO_OUTPUT
                output_parameter.is_data = True

                if 'name' in child.attrib:
                    output_parameter.name = child.attrib['name']

                if 'label' in child.attrib:
                    output_parameter.description = child.attrib['label']

                if 'format' in child.attrib:
                    output_parameter.type = child.attrib['format']

                self.info.outputs.append(output_parameter)

    def _parse_tests(self, node):
        """Parse the test section"""
        for child in node:
            if child.tag == 'test':
                info_test = []
                for sub_child in child:
                    param_info = ToolTestParameterContainer()
                    if sub_child.tag == 'param':
                        param_info.type = 'param'
                        if 'name' in sub_child.attrib:
                            param_info.name = sub_child.attrib['name']
                        if 'value' in sub_child.attrib:
                            param_info.value = sub_child.attrib['value']
                    if sub_child.tag == 'output':
                        param_info.type = 'output'
                        if 'name' in sub_child.attrib:
                            param_info.name = sub_child.attrib['name']
                        if 'file' in sub_child.attrib:
                            param_info.file = sub_child.attrib['file']
                        if 'value' in sub_child.attrib:
                            param_info.value = sub_child.attrib['value']    
                        if 'compare' in sub_child.attrib:
                            param_info.compare = sub_child.attrib['compare']
                    info_test.append(param_info)
                self.info.tests.append(info_test)

    def _parse_categories(self):
        """Parse categories from the .shed.yml file"""
        # get the yml file
        shed_file = os.path.join(os.path.dirname(self.xml_file_url),
                                 '.shed.yml')
        if not os.path.isfile(shed_file):
            return []

        with open(shed_file) as file:
            shed_file_content = yaml.load(file, Loader=yaml.FullLoader)

        return shed_file_content["categories"]
