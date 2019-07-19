# -*- coding: utf-8 -*-
"""BioImagePy core module.

Contains a set of classes and methods for generic usage

Classes
-------
BiObject
BiConfig


"""

import os
import json

class BiObject:
    """Abstract base class for all object used in the BioImagePy package 
    
    The aim of this class is tho have a common basis for all objects in
    the BioImagePy package and share common operations/information.

    Parameters
    ----------
    _objectname
        Name of the object
    """

    def __init__(self):

        self._objectname = "BiObject"           

    def display(self):
        """Display the class information in console
        
        This method should be reimplemented in each subclass in order
        to ba able to display the class content
        """

        print('BiObjectName: ' + self._objectname)
        print('----------------------')
        

class BiProgressObserver(BiObject):
    """Observer to display or log a process progress
    
    The basic implementation just display the progress in the 
    console with 'print'. Please subclass this class to write
    progress in log files or notify a GUI for example
    
    """
    def __init__(self):
        super().__init__()
        self._objectname = "BiObserver"  

    def notify(self, data: dict):
        """Function called by the observable to notify progress

        Parameters
        ----------
        data
            Data descibing the progress
        """

        if 'progress' in data:
            print('progress:', data['progress'])
        if 'message' in data:
            print('message:', data['message'])   
        if 'warning' in data:
            print('warning:', data['warning']) 
        if 'error' in data:
            print('error:', data['error'])         


class BiConfig(BiObject):
    """Class to read/write configuration data
    
    Configuration file must be a json file
    
    """
    def __init__(self, config_file: str):                      
        super().__init__()
        self.config_file = config_file
        self._objectname = "BiConfig"  
        self.config = {}
        self.read()

    def read(self):
        """Read the metadata from the a json file at md_file_url"""
        if os.path.getsize(self.config_file) > 0:
            with open(self.config_file) as json_file:  
                self.config = json.load(json_file)

    def write(self):
        """Write the metadata to the a json file at md_file_url"""
        with open(self.config_file, 'w') as outfile:
            json.dump(self.config, outfile, indent=4) 

    def get_env(self) -> dict:
        if "env" in self.config:
            return self.config['env']
        else:
            print("no env section in ", self.config_file)

    def get_env_map(self):
        env = {}
        if "env" in self.config: 
            for element in self.config['env']:
                env[element["name"]] = element['value']
        return env     

    