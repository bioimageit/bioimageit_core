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
from bioimagepy.data import Data, RawData, ProcessedData

class DataSet():
    """Abstract class that store a dataset metadata
    
    DataSet allows to manipulate the common metadata. This class
    should not be used directly. RawDataSet and ProcessedDataSet
    should be used as specific metadata containers

    Parameters
    ----------
    md_uri
        Uri of the metadata in the database or file system
        depending on backend

    Attributes
    ----------
    name 
        Name of the dataset
    uris
        List of the URIs of the data metadata

    """

    def __init__(self, md_uri : str):

        self.md_uri = md_uri    
        self.name = ''
        self.uris = list() 

    def size(self) -> int:
        """Get the size of the dataset
        
        Returns
        -------
        int
            The size of the dataset 

        """
        return len(self.uris) 
 

class RawDataSet(DataSet):
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
    
    def __init__(self, md_uri : str):
        DataSet.__init__(self, md_uri)

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
        # TODO load from services
        # matadataservice.load_raw_data_from_dataset(md_file, uris[i])
        return RawData('')

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
        # TODO: save data with services and add path to this dataset and save dataset
        # matadataservice.save_data(data)
        # self.uris.append(data.md_file)
        # matadataservice.save_rawdataset(??)   
        pass

    def get_data_list(self) -> list:
        """Get the metadata information as a list
        
        Returns
        -------
        list
            List of the data metadata stored in BiRawData objects

        """
        data_list = []
        for i in range(self.size()):
            # TODO
            # metadataDict = matadataservice.load_raw_data_from_dataset(md_file, uris[i])
            data_list.append(RawData(''))   
        return data_list
      

class ProcessedDataSet(DataSet):
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
    
    def __init__(self, md_uri : str):
        DataSet.__init__(self, md_uri)

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
        # TODO load from services
        # matadataservice.load_processed_data_from_dataset(md_file, uris[i])
        return ProcessedData('')

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
        # TODO: save data with services and add path to this dataset and save dataset
        # matadataservice.save_data(data)
        # self.uris.append(data.md_file)
        # matadataservice.save_rawdataset(??)   
        pass

    def get_data_list(self) -> list:
        """Get the metadata information as a list
        
        Returns
        -------
        list
            List of the data metadata stored in BiRawData objects

        """
        data_list = []
        for i in range(self.size()):
            # TODO
            # metadataDict = matadataservice.load_raw_data_from_dataset(md_file, uris[i])
            data_list.append(ProcessedData(''))   
        return data_list
