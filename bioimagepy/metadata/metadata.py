# -*- coding: utf-8 -*-
"""BioImagePy metadadata definitions.

This module contains the BiMetaData class to read/write
metadata files

Classes
------- 
BiMetaData

"""

import os 
import json
from ..core import core
import errno

class BiMetaData(core.BiObject):
    """Abstract class that store a data metadata
    
    BiMetaData allows to read/write the metadata to file. This class
    should not be used directly.

    Parameters
    ----------
    xml_file_url
        Path of the XML process file

    Attributes
    ----------
    metadata 
        dictionnary containing all the meatadata

    """

    def __init__(self, md_file_url : str):

        self._objectname = "BiMetaData"
        self._md_file_url = md_file_url
        self.metadata = {}
        if os.path.isfile(md_file_url):
            self.read()
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), md_file_url) 

    def md_file_path(self) -> str:
        """get metadata file directory name

        Returns
        ----------
        str
            The name of the metadata file directory

        """
        abspath = os.path.abspath(self._md_file_url)
        return os.path.dirname(abspath)

    def dir(self) -> str:
        """get metadata file directory name

        Returns
        ----------
        str
            The name of the metadata file directory

        """

        abspath = os.path.abspath(self._md_file_url)
        return os.path.dirname(abspath)    

    def read(self):
        """Write the metadata from the a json file at md_file_url"""
        if os.path.getsize(self._md_file_url) > 0:
            with open(self._md_file_url) as json_file:  
                self.metadata = json.load(json_file)

    def write(self):
        """Write the metadata to the a json file at md_file_url"""
        with open(self._md_file_url, 'w') as outfile:
            json.dump(self.metadata, outfile, indent=4)    

    def display(self):
        """Display inherited from BiObject"""

        super(BiMetaData, self).display()  
        