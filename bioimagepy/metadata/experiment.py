# -*- coding: utf-8 -*-
"""experiment module.

This module contains the BiExperiment class that allows to read/write and query
an experiment metadata, and a set of function to manipulate experiment metadata

Example:
    Here is an example of how to create an experiment and add data to it:

        >>> import bioimagepy.metadata.experiment as experiment
        >>>
        >>> myexperiment = experiment.create('myexperiment', 'Sylvain Prigent', './' )
        >>> experiment.import(dirpath, name, author, datatype, createddate=now, copydata=true)
        >>> experiment.import_dir(dirpath, author, datatype, createddate=now, copydata=true, filter=".tif")
        >>> myexperiment.addTag("condition1")
        >>> myexperiment.addTags(["condition1, condition2"])
        >>> myexperiment.display()

Todo:
    * Write a full example in this documentation
    * Write manipulation functions: import, tag...

"""

from .metadata import BiMetaData
from .dataset import BiRawDataSet, BiProcessedDataSet
import os
import errno
import datetime

class BiExperiment(BiMetaData):
    """Class that allows to manipulate experiment metadata.

    A BiExperiment object behave as a container for an experiment 
    metadata. It read only the basic information stored in the 
    experiment.md.json metadata files and methods allows to 
    read/write and manipulate datasets and data information

    Args:
        md_file_url (str): Path of the experiment.md.json file.

    Attributes:
        metadata (tuple): json metadata description.

    """ 
    def __init__(self, md_file_url: str):
        """BiExperiment __init__ method.

        The __init__ method load the experiment metadata if the specified 
        input metadata file exists.

        Args:
            md_file_url (str): The url or path of the experiment metadata file.

        """
        BiMetaData.__init__(self, md_file_url)
        self._objectname = 'BiExperiment'

    def name(self) -> str:
        return self.metadata['information']['name']
  
    def author(self) -> str:
        return self.metadata['information']['author']

    def createddate(self) -> str:
        return self.metadata['information']['createddate']

    def rawsatadet_url(self) -> str:
        return self.metadata['information']['rawdataset']  

    def rawsatadet(self) -> BiRawDataSet:
        return BiRawDataSet( os.path.join(self.md_file_path(), self.metadata['rawdataset']) )

    def processeddatasets_size(self) -> int:
        return len(self.metadata['processeddatasets']) 

    def processeddataset_url(self, i: int) -> str:
        return self.metadata['processeddatasets'][i]  

    def processeddataset_urls(self) -> list:
        return self.metadata['processeddatasets']   

    def processeddataset(self, i: int) -> BiProcessedDataSet:
        return BiRawDataSet( os.path.join(self.md_file_path(), self.metadata['processeddatasets'][i]) )

    def tags_size(self) -> int:
        return len(self.metadata['tags'])

    def tags(self) -> list:
        return self.metadata['tags']

    def tag(self, i: int) -> str:
        return self.metadata['tags'][i]   
           

def create(name: str, author: str, path: str) -> BiExperiment:
    """Create an experiment

    Create an empty experiment in the directory specified in the args
    with the informations given in the args

    Args:
        name (str): The name of the experiment.
        author (str): The name of the person who created the experiment.
        path (str): The directory where the experiment files will be stored.

    Returns:
        BiExperiment: The object containing the experiment.

    Raises:
        FileNotFoundError: if the experiment path does not exists.

    """
    #create the experiment directory
    filtered_name = name.replac(' ', '')
    experiment_path = os.path.join(path, filtered_name)
    if os.path.exists(path):
        os.mkdir( experiment_path )
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

    #create the data directory
    rawdata_path = os.path.join(experiment_path, 'data')
    if os.path.exists(experiment_path):
        os.mkdir( rawdata_path )
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

    #create the experiment metadata
    md_file_url = os.path.join(experiment_path, "experiment.md.json")
    experiment = BiExperiment(md_file_url)
    experiment.metadata['information']['name'] = name
    experiment.metadata['information']['author'] = author
    now = datetime.datetime.now()
    experiment.metadata['information']['createddate'] = now.strftime("%Y-%m-%d")
    experiment.write()

    return experiment
