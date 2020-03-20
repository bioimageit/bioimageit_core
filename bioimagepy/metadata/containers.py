# -*- coding: utf-8 -*-
"""BioImagePy metadata containers.

This module contains containers for metadata Data, Dataset,
Experiment 

Classes
------- 
DataContainer
RawDataContainer
ProcessedDataContainer
DataSetContainer
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

    def serialize(self):
        content = 'name = ' + self.name + '\n' 
        content += 'author = ' + self.author + '\n'
        content += 'date = ' + self.date + '\n'
        content += 'format = ' + self.format + '\n'
        content += 'uri = ' + self.uri + '\n'
        return content     

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

    def serialize(self):
        content = 'RawData:\n'
        content += DataContainer.serialize(self)
        content += 'tags = {'
        for tag in self.tags:
            content += self.tags[tag] + ':' + self.tags[tag] + ','
        content = content[:-1] + '}'
        return content       

class ProcessedDataInputContainer:
    """Container for processed data origin input
    
    Attributes
    ----------
    name
        Name of the input (the unique name in the process)
    uri
        The uri of the input metadata    
    """
    def __init__(self, name:str='', uri:str='', type:str=METADATA_TYPE_RAW()):
        self.name = name
        self.uri = uri
        self.type = type

class ProcessedDataContainer(DataContainer):
    """Metadata container for processed data

    Attributes
    ---------- 
    run_uri
        URI of the Run metadata file
    inputs
        Informations about the inputs that gererated 
        this processed data. It is a list of ProcessedDataInputContainer    
    outputs
        Informations about how the output is references 
        in the process that generates this processed data

    """    
    def __init__(self):
        DataContainer.__init__(self)
        self.run_uri = ''
        self.inputs = list()
        self.output = dict()

    def add_input(self, name:str, uri:str, type:str):
        self.inputs.append(ProcessedDataInputContainer(name, uri, type))  

    def set_output(self, name:str, label:str):
        self.output = {'name':name, 'label':label} 

    def serialize(self):
        content = 'ProcessedData:\n'
        content += DataContainer.serialize(self)
        content += 'run_uri = ' + self.run_uri + '\n'
        content += 'inputs = [ \n'
        for input in self.inputs:
            content += 'name:'+input.name+', uri:'+input.uri+'\n'   
        content += 'output={name:'+self.output['name']+', label:'+self.output['label']+'}'     
        return content     


class DataSetContainer:
    def __init__(self):
        self.name = ''
        self.uris = list()

    def serialize(self):
        content = 'Dataset:\n'
        content += 'name = ' + self.name   
        content += 'uris = \n'
        for uri in self.uris: 
            contnet += '\t' + uri
        content += '\n'            


class ExperimentContainer:
    def __init__(self):
        pass
