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
 
from bioimagepy.metadata.containers import METADATA_TYPE_RAW, RawDataContainer, ProcessedDataContainer, ProcessedDataInputContainer
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

    def set_tag(self, tag_key:str, tag_value:str):
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

    def tag(self, tag_key:str):
        """get a tag value from key

        get a tag in the metadata. It returns and empty
        string if the tag does not exists

        Parameters
        ----------
        tag_key
            Key of the tag to get

        Returns
        -------
        The value of the tag or an empty string is not exists

        """
        if tag_key in self.metadata.tags:
            return self.metadata.tags[tag_key]
        return ''            

    def display(self):
        """Display metadata in console"""
        print(self.metadata.serialize())
        

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
        self.service = metadataServices.get('LOCAL')
        self.read()

    def read(self):
        """Read the metadata from database
        
        The data base connection is managed by the configuration 
        object
        
        """
        self.metadata = self.service.read_processeddata(self.md_uri)
        pass

    def write(self):
        """Write the metadata to database
                
        The data base connection is managed by the configuration 
        object
        
        """
        self.service.write_processeddata(self.metadata, self.md_uri)
        pass   

    def display(self):
        """Display metadata in console"""
        print(self.metadata.serialize())  

    def add_input(self, name:str, uri:str, type:str):
        self.metadata.inputs.append(ProcessedDataInputContainer(name, uri, type))    

    def set_output(self, name:str, label:str):
        self.metadata.output['name'] = name
        self.metadata.output['label'] = label

    def get_parent(self):
        """Get the metadata of the parent data.
        
        The parent data can be a RawData or a ProcessedData 
        depending on the process chain

        Returns
        -------
        parent
            Parent data (RawData or ProcessedData)
        
        """
        
        if len(self.metadata.inputs) > 0:
            
            if self.metadata.inputs[0].type == METADATA_TYPE_RAW():
                return RawData(self.metadata.inputs[0].uri)
            else:
                return ProcessedData(self.metadata.inputs[0].uri)  
        return None        

    def get_origin(self) -> RawData:
        """Get the first metadata of the parent data.

        The origin data is a RawData. It is the first data that have 
        been seen by bioimagepy

        Returns
        -------
        the origin data in a RawData object

        """
        return processed_data_origin(self)

# queries
def processed_data_origin(processed_data:ProcessedData):
    if len(processed_data.metadata.inputs) > 0:
        if processed_data.metadata.inputs[0].type == METADATA_TYPE_RAW():
            return RawData(processed_data.metadata.inputs[0].uri)
        else:
            return processed_data_origin(ProcessedData(processed_data.metadata.inputs[0].uri))