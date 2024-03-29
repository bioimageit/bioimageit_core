# -*- coding: utf-8 -*-
"""toolboxes module.
This module contains tools to build the toolbox wrappers database.
It reads the tools.json file in the toolboxes folder (from 
https://gitlab.inria.fr/bioimage-it/toolboxes) and download the
wrappers in the tools/ directory
Example
-------
    Toolboxes can be use from puthon3:
        >>> builder = Toolboxes() 
        >>> builder.build() 
    or run from the command line. 
    With default config file  
        $ python3 bioimagepy/toolboxes.py 
    with custom config file url  
        $ python3 bioimagepy/toolboxes.py /config/file/path.json 
    In both cases, the toolbox path is read from the config 
    file (config.json)    
                                       
Classes
-------
Toolboxes
        
"""

import os
import json
import wget
from zipfile import ZipFile
import shutil
import glob

from .observer import Observable
from .config import ConfigAccess


class ToolboxesError(Exception):
    """Raised when an error happen in the toolboxes management"""

    pass


def _recursive_move(source_dir, destination):
    files = glob.iglob(os.path.join(source_dir, "*.*"))
    for file in files:
        if os.path.isfile(file):
            shutil.move(file, destination)
    files = glob.iglob(os.path.join(source_dir, ".*"))
    for file in files:
        if os.path.isfile(file):
            shutil.move(file, destination)


class Toolboxes(Observable):
    def __init__(self):
        super().__init__()
        config = ConfigAccess.instance().config['process']
        self.xml_dir = config['xml_dirs'][0]
        self.tools_file = config['tools']

    def build(self):

        # verify that the xml_dir exists
        # read toolbox_file to json
        # foreach tooldir
        #     copy local
        #     clean
        self._check_xml_dir()
        tools = self._read_tools_file()
        for tool in tools:
            self._import_tool(tool)

    def _check_xml_dir(self):
        if not os.path.isdir(self.xml_dir):
            os.mkdir(self.xml_dir)
        if not os.path.isdir(self.xml_dir):
            raise ToolboxesError(
                'Cannot create the tools directory for toolboxes')

    def _read_tools_file(self):
        if os.path.getsize(self.tools_file) > 0:
            with open(self.tools_file) as json_file:
                return json.load(json_file)["tools"] 

    def _find_tools_subfolder(self, dir):
        for root, subFolder, files in os.walk(dir):
            if ('tools' in subFolder):
                return os.path.join(root, 'tools')
        return ''        

    def _import_tool(self, tool):
        if "url" not in tool or "name" not in tool:
            print(
                "Warning one entry does not has 'url' or 'name' tag is ignored")
            self.notify_observers(
                0,
                "Warning one entry does not has 'url' or 'name' tag is ignored"
            )
            return

        # create dir
        tool_dir = os.path.join(self.xml_dir, tool["name"])
        if not os.path.isdir(tool_dir):
            os.mkdir(tool_dir)

        # download
        tool_zip = os.path.join(self.xml_dir, tool["name"], 'tmp.zip')
        wget.download(tool["url"], tool_zip)
        print()

        # extract
        with ZipFile(tool_zip, 'r') as zipObj:
            zipObj.extractall(tool_dir)

        # copy tools to /tools
        tool_dir_tool = self._find_tools_subfolder(tool_dir)
        if tool_dir_tool != '':
            for root, subFolder, files in os.walk(tool_dir_tool):
                if (root.endswith('tools')):
                    for subFold in subFolder:
                        source = os.path.join(root, subFold)
                        destination = os.path.join(self.xml_dir, subFold)
                        shutil.move(source, destination)

        # remove 
        shutil.rmtree(tool_dir)