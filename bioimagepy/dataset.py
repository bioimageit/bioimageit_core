# -*- coding: utf-8 -*-
"""BioImagePy dataset metadata definitions.

This module contains classes that allows to describe the
metadata of scientific dataset 

Classes
------- 
DataSet
RawDataSet
ProcessedDataSet

"""

import os
from bioimagepy.data import RawData, ProcessedData
from bioimagepy.metadata.factory import metadataServices

class RawDataSet():
    """Class that store a dataset metadata for RawDataSet
  
    Parameters
    ----------
    md_uri
        URI of the metadata in the database or file system
        depending on backend

    Attributes
    ----------
    name 
        Name of the dataset
    uris
        List of the URIs of the data metadata

    """
    
    def __init__(self, md_uri : str = ''):
        self.md_uri = md_uri   
        self.metadata = None # DataSetContainer()
        self.service = metadataServices.get('LOCAL')
        self.read()

    def read(self):
        """Read the metadata from database
        
        The data base connection is managed by the configuration 
        object
        
        """
        self.metadata = self.service.read_rawdataset(self.md_uri)

    def write(self):
        """Write the metadata to database
                
        The data base connection is managed by the configuration 
        object
        
        """
        self.service.write_rawdataset(self.metadata, self.md_uri)     

    def size(self):
        """get the size of the dataser

        Returns
        -------
        The number of data in the dataset

        """
        return len(self.metadata.uris)

    def get(self, i: int) -> RawData:
        """get one data information
        
        Parameters
        ----------
        i
            Index of the data in the dataset

        Returns
        ----------
        RawData
            The data common information 

        """
        return RawData(self.metadata.uris[i])

    def get_data(self, filter:str):
        """get one data information

        The data is selected using a filter on the name
        
        Parameters
        ----------
        filter
            Filter on the name. Ex: name="myimage.tif"
            Any regular expression can be use

        Returns
        ----------
        RawData
            The data common information 

        """
        # TODO load from services
        # matadataservice.load_processed_data_from_dataset(md_file, uris[i])
        return RawData('')    

    def add_data(self, data: RawData):
        """Add one data to the dataset
        
        Parameters
        ----------
        data
            data to add

        """
        data.write()
        self.metadata.uris.append(data.md_uri)
        self.service.write_rawdataset(self.metadata, self.md_uri)

    def get_data_list(self) -> list:
        """Get the metadata information as a list
        
        Returns
        -------
        list
            List of the data metadata stored in BiRawData objects

        """
        data_list = []
        for i in range(self.size()):
            data_list.append(RawData(self.metadata.uris[i]))   
        return data_list
      

class ProcessedDataSet():
    """Class that store a dataset metadata for ProcessedDataSet
  
    Parameters
    ----------
    md_uri
        URI of the metadata in the database or file system
        depending on backend

    Attributes
    ----------
    name 
        Name of the dataset
    uris
        List of the URIs of the data metadata

    """
    
    def __init__(self, md_uri : str = ''):
        self.md_uri = md_uri   
        self.metadata = None # DataSetContainer()
        self.service = metadataServices.get('LOCAL')
        self.read()

    def read(self):
        """Read the metadata from database
        
        The data base connection is managed by the configuration 
        object
        
        """
        self.metadata = self.service.read_processeddataset(self.md_uri)

    def write(self):
        """Write the metadata to database
                
        The data base connection is managed by the configuration 
        object
        
        """
        self.service.write_processeddataset(self.metadata, self.md_uri)  

    def size(self):
        """get the size of the dataser

        Returns
        -------
        The number of data in the dataset

        """
        return len(self.metadata.uris)

    def get(self, i: int) -> ProcessedData:
        """get one data information
        
        Parameters
        ----------
        i
            Index of the data in the dataset

        Returns
        ----------
        RawData
            The data common information 

        """
        return ProcessedData(self.metadata.uris[i])

    def get_data(self, filter:str):
        """get one data information

        The data is selected using a filter on the name
        
        Parameters
        ----------
        filter
            Filter on the name. Ex: name="myimage.tif"
            Any regular expression can be use

        Returns
        ----------
        ProcessedData
            The data common information 

        """
        # TODO load from services
        # matadataservice.load_processed_data_from_dataset(md_file, uris[i])
        return ProcessedData('')


    def add_data(self, data: ProcessedData):
        """Add one data to the dataset
        
        Parameters
        ----------
        data
            data to add

        """
        data.write()
        self.metadata.uris.append(data.md_uri)
        self.service.write_processeddataset(self.metadata, self.md_uri)

    def get_data_list(self) -> list:
        """Get the metadata information as a list
        
        Returns
        -------
        list
            List of the data metadata stored in BiRawData objects

        """
        data_list = []
        for i in range(self.size()):
            data_list.append(ProcessedData(self.metadata.uris[i]))   
        return data_list
