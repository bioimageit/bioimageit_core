# -*- coding: utf-8 -*-
"""experiment module.

This module contains the Experiment class that allows to read/write and query
an experiment metadata.

Example
-------
    Here is an example of how to create an experiment and add data to it:

        >>> from bioimagepy.experiment import Experiment
        >>> myexperiment = Experiment()
        >>> myexperiment.create('myexperiment', 'Sylvain Prigent', './')
        >>> myexperiment.import_data(uri='data_uri', name='mydata', author='Sylvain Prigent', dataformat='tif', createddata='now', copy_data=True)
        >>> myexperiment.import_dir(dir_uri='./my/local/dir/', author='Sylvain Prigent', dataformat='tif', createddate='now', copy_data=True)
        >>> myexperiment.tag_from_name(tag='population', ['population1', 'population2'])
        >>> myexperiment.tag_using_seperator(tag='ID', separator='_', value_position=1)
        >>> myexperiment.display()

Classes
-------
Experiment


TODO:
    Add methods:
        add_tag(name:str)
        
"""

from bioimagepy.data import RawData, ProcessedData
from bioimagepy.dataset import RawDataSet, ProcessedDataSet

class Experiment():
    def __init__(self, md_uri=''):
        self.md_uri = md_uri

    def create(self, name: str, author: str, uri: str):
        """Create a new experiment
        
        The create method initialize a new experiment with
        the main metadata architecture
        
        Parameters
        ----------
        name
            Name of the experiment
        author
            Name of the person who created the experiment
        uri
            URI of the experiment. For local it is the directory
            where the experiment will be saved. For Omero, it is the
            user workspace        

        """
        # TODO call the factory/services to create 
        #experimentfactory.create(name, author, uri)        
        pass

    def import_dir(self, dir_uri:str, filter:str, author:str, dataformat:str, createddate:str, copy_data:bool):
        """Import data from a directory to the experiment
        
        This method import with or whitout copy data contained 
        in a local folder into an experiment. Imported data are
        considered as RawData for the experiment
        
        Parameters
        ----------
        dir_uri
            URI of the directory containing the data to be imported
        filter
            Regular expression to filter which files in the folder 
            to import    
        author
            Name of the person who created the data
        createddate
            Date when the data where created
        copy_data
            True to copy the data to the experiment, false otherwise. If the
            data are not copied, an absolute link to dir_uri is kept in the
            experiment metadata. The original data directory must then not be
            changed for the experiment to find the data.        

        """
        # ExperimentFactory.import_dir(dir_uri, filter, author, dataformat, createddate, copy_data)
        pass

    def display(self, dataset:str='data'):
        """Display a dataset content as a table in the console

        Parameters
        ----------        
        dataset
            Name of the dataset to display
        
        """
        # ExperimentFactory.display(dataset)
        pass

    def tag_from_name(self, tag: str, values: list)
        """Tag an experiment raw data using file name

        Parameters
        ----------
        tag
            The name (or key) of the tag to add to the data
        values
            List of possible values for the tag to find in the filename    

        """
        # ExperimentFactory.tag_from_name(tag, value)
        pass


    def tag_using_seperator(tag: str, separator: str, value_position: int):
        """Tag an experiment raw data using file name and separator

        Parameters
        ----------
        tag
            The name (or key) of the tag to add to the data
        separator
            The character used as a separator in the filename (ex: _)    
        value_position
            Position of the value to extract with respect to the separators    

        """    
        # ExperimentFactory.tag_from_separator(tag, separator, value_position)
        pass

    def get_dataset(self, name:str):
        """Get the metadata of a dataset

        Returns a RawDataset or a ProcessedDataSet

        Parameters
        ----------
        name
            Name of the dataset

        """
        # ExperimentFactory.get_dataset(name)
        pass

    def get_data(self, dataset:str, filter:str):
        """Get the metadata of a data

        Returns a RawData or a ProcessedData

        Parameters
        ----------
        dataset
            Name of the dataset
        filter
            Filter on the data name. Ex: name=myimage.tif    

        Returns
        -------
        data
            A RawData or a ProcessedData if the data is found.
            None otherwise 

        """
        # ExperimentFactory.get_dataset(name)
        pass