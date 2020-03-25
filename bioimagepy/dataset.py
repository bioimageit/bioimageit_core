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
import re

from bioimagepy.config import ConfigAccess
from bioimagepy.data import RawData, ProcessedData
from bioimagepy.metadata.factory import metadataServices
from bioimagepy.metadata.query import query_list_single
from bioimagepy.metadata.containers import SearchContainer

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
        config = ConfigAccess.instance().config['metadata']
        self.service = metadataServices.get(config["service"], **config)
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

    def to_search_containers(self):
        """Convert RawDataSet into a list of SearchContainer

        Returns
        -------
        list
            List of data as list of SearchContainer    

        """
        search_list = []
        for i in range(self.size()):
            data = RawData(self.metadata.uris[i])
            search_list.append(data.to_search_container())  
        return search_list  

    def get_data(self, query: str) -> list:
        """query on tags
        
        In this verion only AND queries are supported (ex: tag1=value1 AND tag2=value2)
        and performed on the RawData set

        Parameters
        ----------
        rawdataset
            The RawDataSet to query.
        query
            String query with the key=value format. 

        Returns
        -------
        list
            List of selected data (md.json files urls are returned)       
        
        """
        
        queries = re.split(' AND ',query)

        # initially all the rawdata are selected
        selected_list = self.to_search_containers()

        if query == '':
            return selected_list

        # run all the AND queries on the preselected dataset
        for q in queries:
            selected_list = query_list_single(selected_list, q) 

        # convert SearchContainer list to uri list
        out = []
        for d in selected_list:
            out.append(d.uri())
        return out            

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
        config = ConfigAccess.instance().config['metadata']
        self.service = metadataServices.get(config["service"], **config)
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

    def to_search_containers(self):
        """Convert RawDataSet into a list of SearchContainer

        Returns
        -------
        list
            List of data as list of SearchContainer    

        """
        search_list = []
        for i in range(self.size()):
            data = ProcessedData(self.metadata.uris[i])
            search_list.append(data.to_search_container())  
        return search_list

    def get_data(self, query: str, origin_output_name: str = '') -> list:
        """Run a query on a BiProcessedDataSet

        Parameters
        ----------
        query
            Query on tags (ex: 'Population'='population1')
        origin_output_name
            Filter only the process output with the given name
            if origin_output_name is empty, it gets all the processed
            data      

        Returns
        -------
        list
            List of the data URIs        

        """

        # get all the tags per data
        pre_list = self.to_search_containers()

        # remove the data where output origin is not the asked one
        selected_list = []
        if origin_output_name != '':
            for pdata in pre_list:
                data = ProcessedData(pdata.url())
                if data.metadata.output["name"] == origin_output_name:
                    selected_list.append(pdata) 
        else:
            selected_list = pre_list

        if query == '':
            return selected_list

        # query on tags
        queries = re.split(' AND ',query)

        # run all the AND queries on the preselected dataset
        for q in queries:
            selected_list = query_list_single(selected_list, q) 
        
        # convert SearchContainer list to uri list
        out = []
        for d in selected_list:
            out.append(d.uri())
        return out   


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
