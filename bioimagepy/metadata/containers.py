# -*- coding: utf-8 -*-
"""BioImagePy metadata containers.

This module contains containers for metadata Data, Dataset,
Experiment 

Classes
------- 
DataContainer
RawDataContainer
ProcessedDataContainer
DatasetContainer
RawDataSetContainer
ProcessedDataSetContainer
ExperimentContainer

"""

def METADATA_TYPE_RAW():
    """Type for matadata for raw data""" 
    return "raw"

def METADATA_TYPE_PROCESSED():
    """Type for matadata for processed data""" 
    return "processed"   

class DataContainer:
    """Metadata container for generic data
    
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
    def __init__(self):
        self.name = ''
        self.author = ''
        self.date = ''
        self.format = ''
        self.uri = ''

class RawDataContainer(DataContainer):
    """Metadata container for raw data
    
    Attributes
    ----------
    tags
        Dictionnary containing the tags (key=value)
    
    """
    def __init__(self):
        DataContainer.__init__(self)
        self.tags = dict()

class ProcessedDataContainer(DataContainer):
    """Metadata container for processed data

    Attributes
    ---------- 
    run_uri
        URI of the Run metadata file
    inputs
        Informations about the inputs that gererated 
        this processed data    
    outputs
        Informations about how the output is references 
        in the process that generates this processed data

    """    
    def __init__(self):
        DataContainer.__init__(self)
        self.run_uri = ''
        self.inputs = dict()
        self.outputs = dict()

class DatasetContainer:
    def __init__(self):
        pass

class RawDataSetContainer:
    def __init__(self):
        pass

class ProcessedDataSetContainer:
    def __init__(self):
        pass

class ExperimentContainer:
    def __init__(self):
        pass
