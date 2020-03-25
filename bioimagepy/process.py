# -*- coding: utf-8 -*-
"""BioImagePy process info management.

This module implement utilities to manage the processes.
- Read process info from xml file
- create a dictionnary of processed 

TODO
----
Add example of class usage

Methods
-------
PARAM_NUMBER
PARAM_STRING
PARAM_SELECT
PARAM_BOOLEAN
PARAM_HIDDEN
PARAM_FILE
IO_PARAM
IO_INPUT
IO_OUTPUT

Classes
------- 
CmdSelect
ProcessParameter
ProcessMainInfo
ProcessInfo
ProcessParser
ProcessDatabase

""" 

import os
import xml.etree.ElementTree as ET

from bioimagepy.processes.containers import ProcessContainer
from bioimagepy.processes.factory import processServices
from bioimagepy.config import ConfigAccess

class Process():
    """Interact with a process info

    Process allows to read/write and manipulate the metadata
    of a process.

    Parameters
    ----------
    md_uri
        URI of the metadata in the database or file system
        depending on backend

    Attributes
    ----------
    metadata 
        Container of the metadata       

    """
    def __init__(self, uri: str):
        self.uri = uri
        config = ConfigAccess.instance().config['process']
        self.service = processServices.get(config['service'], **config)
        self.metadata = self.service.read_process(self.uri)  

    def man(self):
        """Display the process man page"""
        # 1. program name
        print(self.metadata.name, ':', self.metadata.description)
        # 2. list of args key, default, description
        for param in self.metadata.inputs:
            line_new = '\t{:>15}\t{:>15}\t{:>15}'.format(param.name, param.default_value, param.description)
            print(line_new)
        for param in self.metadata.outputs:
            line_new = '\t{:>15}\t{:>15}\t{:>15}'.format(param.name, param.default_value, param.description)
            print(line_new) 


class ProcessAccess():
    """To request the processed database"""
    def __init__(self):
        config = ConfigAccess.instance().config['process']
        self.service = processServices.get(config['service'], **config)               
            
    def search(self, keyword:str):
        """Search a process using a keyword in the database
        
        This method print the list of funded processed

        Parameters
        ----------
        keyword
            Keyword to search in the database  
        
        """
        plist = self.service.search(keyword)
        for process in plist:
            print(process.serialize('h'))

    def get(self, name:str) -> Process:
        """get a process by name
        
        Parameters
        ----------
        name
            Fullname of the process ({name}_v{version})
        
        Returns
        -------
        An instance of the process

        """        
        uri = self.service.get_process(name)
        return Process(uri)
        