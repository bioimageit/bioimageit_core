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
Process
        
"""

import sys
import os
import json
import wget
from zipfile import ZipFile
import shutil
import glob

from bioimagepy.core.utils import Observable
from bioimagepy.config import ConfigAccess


class ToolboxesError(Exception):
    """Raised when an error happen in the tollboxes management"""

    pass


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
            raise ToolboxesError('Cannot create the tools directory for toolboxes')

    def _read_tools_file(self):
        if os.path.getsize(self.tools_file) > 0:
            with open(self.tools_file) as json_file:
                return json.load(json_file)["tools"]

    def _import_tool(self, tool):

        if not "url" in tool or not "name" in tool:
            print("Warning one entry does not has 'url' or 'name' tag is ignored")
            self.notify_observers(
                0, "Warning one entry does not has 'url' or 'name' tag is ignored"
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

        # clean
        tool_dir_tool = os.path.join(tool_dir, "tools")
        if not os.path.isdir(tool_dir_tool):
            os.mkdir(tool_dir_tool)
        files = glob.glob(tool_dir + '**/**', recursive=True)
        for file in files:
            if file.endswith('/tools') and file != tool_dir_tool:
                self.recursive_move(file, tool_dir_tool)
        tool_dir_files = os.listdir(tool_dir)
        for file in tool_dir_files:
            if file != 'tools':
                file_path = os.path.join(tool_dir, file)
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)

    def recursive_move(self, source_dir, destination):
        files = glob.iglob(os.path.join(source_dir, "*.*"))
        for file in files:
            if os.path.isfile(file):
                shutil.move(file, destination)
        files = glob.iglob(os.path.join(source_dir, ".*"))
        for file in files:
            if os.path.isfile(file):
                shutil.move(file, destination)
