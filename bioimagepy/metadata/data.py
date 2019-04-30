# -*- coding: utf-8 -*-
"""BioImagePy data definitions.

This module contains three classed that allows to describe the
metadata of scientific data

Classes
------- 
BiData
BiRawData
BiProcessedData

"""

from .metadata import BiMetaData
import os

class BiData(BiMetaData): 
    """Abstract class that store a data metadata
    
    BiData allows to manipulate the common metadata. This class
    should not be used directly. BiRawData and BiProcessedData
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
        self._objectname = "BiData"  

    def url(self) -> str:
        """get the data file
        
        This function returns the obsolute full path (or url) of 
        the data file. It is computed usting the metadata file path 

        Returns
        ----------
        str
            The path (or url) of the metadata file 

        """

        file = self.metadata["common"]['url']
        if os.path.isfile(file):
            return file
        else:    
            return os.path.join(self.md_file_path(), file)

    def url_as_stored(self) -> str:
        """get the data file
        
        This function returns the data file path as stored in the 
        metadata file. This path can be relative or absolute depending
        on how the metadata file was filled

        Returns
        ----------
        str
            The path (or url) of the metadata file 

        """

        return self.metadata["common"]['url']   

    def name(self) -> str:
        """get the data name

        Returns
        ----------
        str
            The data name

        """

        return self.metadata["common"]['name']  

    def author(self) -> str:
        """get the author name

        Returns
        ----------
        str
            The author name

        """

        return self.metadata["common"]['author']   

    def createddate(self) -> str:
        """get the created date

        Returns
        ----------
        str
            The created date

        """

        return self.metadata["common"]['createddate']          

    def display(self):
        """Display inherited from BiObject"""

        super(BiData, self).display()  
        print('Data: ' + self._md_file_url)
        print('Common ---------------')
        print('Name: ' + self.metadata["common"]['name'])
        print('Url: ' + self.metadata["common"]['url'])
        print('Author: ' + self.metadata["common"]['author'])
        print('Datatype: ' + self.metadata["common"]['datatype'])
        print('Created Date: ' + self.metadata["common"]['createddate'])
        print('Origin ---------------')    
        print('Type: ' + self.metadata["origin"]['type'])
        

class BiRawData(BiData):
    """Class to store and manipulate RawData metadata
  
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

        self._objectname = "BiRawData"
        BiData.__init__(self, md_file_url)

    def tag(self, key: str):
        """get a tag value

        Parameters
        ----------
        key
            Tag name

        Returns
        ----------
        str
            The tag value for tag key

        """

        if 'tags' in self.metadata:
            if key in self.metadata['tags']:
                return self.metadata['tags'][key]
        return ''  

    def set_tag(self, key: str, value: str):
        """modify a tag or create it if not exists

        Parameters
        ----------
        key
            The tag name
        value
            The tag value

        """

        if 'tags' not in self.metadata:
            self.metadata['tags'] = dict()
        self.metadata['tags'][key] = value

    def display(self): 
        """Display inherited from BiObject"""

        super(BiRawData, self).display()
        print("tag:")
        if 'tags' in self.metadata:
            for key, values in self.metadata["tags"]:
                print(key, ":", value)
        print('')

class BiProcessedData(BiData):
    """Class to store and manipulate RawData metadata
  
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

        self._objectname = "BiProcessedData"
        BiData.__init__(self, md_file_url)

    def display(self): 
        """Display inherited from BiObject"""

        super(BiProcessedData, self).display()  
        print('Runurl: ' + self.metadata["origin"]['runurl'])
        print('')
 