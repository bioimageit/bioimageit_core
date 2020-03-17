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

def METADATA_TYPE_NONE():
    """Type for matadata for unisignalized data""" 
    return "none"

def METADATA_TYPE_RAW():
    """Type for matadata for raw data""" 
    return "raw"

def METADATA_TYPE_PROCESSED():
    """Type for matadata for processed data""" 
    return "processed"    

class Data():
    """Abstract class that store a data metadata
    
    Data allows to manipulate the common metadata. This class
    should not be used directly. RawData and ProcessedData
    should be used as specific metadata containers

    Parameters
    ----------
    md_uri
        URI of the metadata in the database or file system
        depending on backend

    Attributes
    ----------
    name 
        Name of the data
    author
        Author of the data 
    date
        Date when the data is created
    format
        Data format (txt, csv, tif, ...)
    uri
        URI of the data as stored in the database        

    """

    def __init__(self, md_uri: str):
        # info
        self.md_uri = md_uri
        self.type = METADATA_TYPE_NONE()
        # config
        self._config = '' # TODO Read from singleton
        # common metadata
        self.name = ''
        self.author = ''
        self.date = ''
        self.format = ''
        self.uri = ''

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
    name 
        Name of the data
    author
        Author of the data 
    date
        Date when the data is created
    format
        Data format (txt, csv, tif, ...)
    uri
        URI of the data as stored in the database 
    absolute_uri
        URI of the data        

    """
    def __init__(self, md_uri: str):
        Data.__init__(self, md_uri)   
        self.type = METADATA_TYPE_RAW()

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
        # TODO write from write services  
        pass 

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
    name 
        Name of the data
    author
        Author of the data 
    date
        Date when the data is created
    format
        Data format (txt, csv, tif, ...)
    uri
        URI of the data as stored in the database 
    absolute_uri
        URI of the data  
    run_uri
        URI of the Run metadata file
    inputs
        Informations about the inputs that gererated 
        this processed data    
    outputs
        Informations about how the output is references 
        in the process that generates this processed data

    """

    def __init__(self, md_uri: str): 
        Data.__init__(self, md_uri)
        self.type = METADATA_TYPE_PROCESSED()
        # processed metadata
        self.run_uri = ''
        self.inputs = dict()
        self.outputs = dict()

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
