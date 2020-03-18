# -*- coding: utf-8 -*-
"""BioImagePy Data definitions.

This module contains classes that to manimpulate scientific
data metadata using RawData and ProcessedData 

Classes
------- 
Data
RawData
ProcessedData

"""

import os
 
from bioimagepy.metadata.containers import RawDataContainer, ProcessedDataContainer
from bioimagepy.metadata.factory import metadataServices

class RawData():
    """Class that store a raw data metadata
    
    RawData allows to read/write and manipulate the metadata
    of a raw data.

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
    def __init__(self, md_uri: str):
        self.md_uri = md_uri   
        self.metadata = None # RawDataContainer()
        self.service = metadataServices.get('LOCAL')
        self.read()

    def read(self):
        """Read the metadata from database
        
        The data base connection is managed by the configuration 
        object
        
        """
        self.metadata = self.service.read_rawdata(self.md_uri)

    def write(self):
        """Write the metadata to database
                
        The data base connection is managed by the configuration 
        object
        
        """
        self.service.write_rawdata(self.metadata, self.md_uri)  

    def tag(self, tag_key:str, tag_value:str):
        """Set a tag to the data
        
        If the tag key does not exists for this data, it is 
        created. If the tag key exists the value is changed

        Parameters
        ----------
        tag_key
            Key of the tag
        tag_value
            Value of the tag    
        
        """
        self.metadata.tags[tag_key] = tag_value
        self.service.write(self.metadata, self.md_uri)  

    def display(self):
        """Display metadata in console"""
 
        print('Data: ' + self.md_uri)
        print('Origin ---------------')    
        print('Type: ' + self.metadata.type) 
        print('Common ---------------')
        print('Name: ' + self.metadata.name)
        print('Url: ' + self.metadata.uri)
        print('Author: ' + self.metadata.author)
        print('Format: ' + self.metadata.format)
        print('Created Date: ' + self.metadata.date)
        print('Tags ---------------')
        for key in self.metadata.tags:
            print(key + ': ' + self.metadata.tags[key])
    

class ProcessedData():
    """Class that store a raw data metadata
    
    RawData allows to read/write and manipulate the metadata
    of a raw data.

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

    def __init__(self, md_uri: str): 
        self.md_uri = md_uri   
        self.metadata = None #ProcessedDataContainer()
        self.read()

    def read(self):
        """Read the metadata from database
        
        The data base connection is managed by the configuration 
        object
        
        """
        # TODO read from read services
        pass

    def write(self):
        """Write the metadata to database
                
        The data base connection is managed by the configuration 
        object
        
        """
        # TODO write from write services  
        pass     

    def get_parent(self):
        """Get the metadata of the parent data.
        
        The parent data can be a RawData or a ProcessedData 
        depending on the process chain
        
        """
        # TODO
        pass    

    def get_origin(self):
        """Get the first metadata of the parent data.

        The origin data is a RawData. It is the first data that have 
        been seen by bioimagepy

        Returns
        -------
        the origin data in a RawData object

        """
        # TODO
        pass
