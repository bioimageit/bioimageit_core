# -*- coding: utf-8 -*-
"""BioImagePy dataset definitions.

This module contains three classed that allows to describe the
metadata of scientific dataset

Classes
------- 
BiDataSet
BiRawDataSet
BiProcessedDataSet

"""

from .metadata import BiMetaData
from .data import BiData, BiRawData, BiProcessedData
import os

class BiDataSet(BiMetaData):
    """Abstract class that store a dataset metadata
    
    BiDataSet allows to manipulate the common metadata. This class
    should not be used directly. BiRawDataSet and BiProcessedDataSet
    should be used as specific metadata containers

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

        BiMetaData.__init__(self, md_file_url)
        self._objectname = "BiDataSet"

    def name(self) -> str:
        """get the name of the dataset
        
        Returns
        ----------
        str
            The name of the dataset 

        """

        if 'name' in self.metadata:
            return self.metadata["name"]
        else:
            return ''

    def size(self) -> int:
        """get the size of the dataset
        
        Returns
        ----------
        str
            The size of the dataset 

        """

        if 'urls' in self.metadata:
            return len(self.metadata["urls"]) 
        else:
            return 0

    def urls(self) -> list:
        """get the data urls
        
        Returns
        ----------
        list
            The list of the data urls 

        """

        if 'urls' in self.metadata:
            return self.metadata["urls"]
        else:
            return []    

    def url(self, i: int) -> str:
        """get one data url
        
        Parameters
        ----------
        i
            Index of the data in the dataset

        Returns
        ----------
        str
            The data url 

        """

        return self.metadata["urls"][i]

    def data(self, i: int) -> BiData:
        """get one data information
        
        Parameters
        ----------
        i
            Index of the data in the dataset

        Returns
        ----------
        BiData
            The data common information 

        """

        return BiData(os.path.join(self.md_file_path(), self.url(i)))  


class BiRawDataSet(BiDataSet):
    """Class that store a dataset metadata for RawData
  
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
        BiDataSet.__init__(self, md_file_url)
        self._objectname = 'BiRawDataSet'

    def raw_data(self, i: int) -> BiRawData:
        """get one data information
        
        Parameters
        ----------
        i
            Index of the data in the dataset

        Returns
        ----------
        BiRawData
            The data common information 

        """

        return BiRawData(os.path.join(self.md_file_path(), self.url(i)))
 
    def add_data(self, md_file_url: str):
        """Add one data to the dataset
        
        Parameters
        ----------
        md_file_url
            Path of the metadata file

        """

        if 'urls' in self.metadata:
            self.metadata['urls'].append(md_file_url)
        else:
            self.metadata['urls'] = [md_file_url]    

    def to_list(self) -> list:
        """Get the metadata information as a list
        
        Returns
        -------
        list
            List of the data metadata stored in BiRawData objects

        """

        data_list = []
        for i in range(self.size()):
            data_list.append(BiRawData(os.path.join(self.md_file_path(), self.url(i))))   
        return data_list


class BiProcessedDataSet(BiDataSet):
    """Class that store a dataset metadata for ProcessedData
  
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

        BiDataSet.__init__(self, md_file_url)
        self._objectname = "BiProcessedDataSet"    

    def processed_data(self, i: int) -> BiProcessedData:
        """Get the metadata information as a list
        
        Returns
        -------
        list
            List of the data metadata stored in BiProcessedData objects

        """

        return BiProcessedData(os.path.join(self.md_file_path(), self.url(i)))        
        