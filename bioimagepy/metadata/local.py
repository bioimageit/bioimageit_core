# -*- coding: utf-8 -*-
"""BioImagePy local metadata service.

This module implements the local service for metadata
(Data, DataSet and Experiment) management.
This local service read/write and query metadata from a database
made od JSON file in the file system  

Classes
------- 
MetadataServiceProvider

"""

import os
import os.path
import json

from bioimagepy.metadata.containers import (METADATA_TYPE_RAW, METADATA_TYPE_PROCESSED, 
                                            RawDataContainer, ProcessedDataContainer,
                                            ProcessedDataInputContainer, DataSetContainer)


def md_file_path(md_uri:str) -> str:
    """get metadata file directory path

    Returns
    ----------
    str
        The name of the metadata file directory path

    """
    abspath = os.path.abspath(md_uri)
    return os.path.dirname(abspath)

def relative_path(file:str, reference_file:str):
    """convert file absolute path to a relative path wrt reference_file

    Parameters
    ----------
    reference_file
        Reference file 
    file
        File to get absolute path   

    Returns
    -------
    relative path of uri wrt md_uri  

    """
    separator = os.sep
    file = file.replace(separator+separator, separator)
    reference_file = reference_file.replace(separator+separator, separator)

    for i in range(len(file)):
        common_part = reference_file[0:i]
        if not common_part in file:
            break

    last_separator = common_part.rfind(separator)

    shortreference_file = reference_file[last_separator+1:]

    numberOfSubFolder = shortreference_file.count(separator)
    shortfile = file[last_separator+1:]
    for i in range(numberOfSubFolder):
        shortfile = '..' + separator + shortfile

    return shortfile

def absolute_path(file:str, reference_file:str):
    """convert file relative ro referenceFilte into an absolut path

    Parameters
    ----------
    reference_file
        Reference file 
    file
        File to get absolute path   

    Returns
    -------
    relative path of uri wrt md_uri  

    """
    if os.path.isfile(file):
        return os.path.abspath(file)

    separator = os.sep
    last_separator = reference_file.rfind(separator)    
    canonical_path = reference_file[0:last_separator+1]
    return simplify_path(canonical_path + file)

def simplify_path(path:str) -> str:
    """Simplify a path by removing ../"""

    if path.find('..') < 0:
        return path

    separator = os.sep
    keep_folders = path.split(separator)

    found = True
    while found:
        pos = -1
        folders = keep_folders
        for i in range(len(folders)):
            if folders[i] == '..':
                pos = i
                break    
        if pos > -1:  
            keep_folders = []  
            for i in range(0,pos-1):  
                keep_folders.append(folders[i])
            for i in range(pos+1,len(folders)):
                keep_folders.append(folders[i])
        else:
            found = False        

    clean_path = ''
    for i in range(len(keep_folders)):
        clean_path += keep_folders[i] 
        if i < len(keep_folders)-1:
            clean_path += separator     
    return clean_path


class LocalMetadataServiceBuilder:
    """Service builder for the metadata service"""
    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = LocalMetadataService()
        return self._instance

class LocalMetadataService:
    """Service for local metadata management

    """
    def __init__(self):
        self.service_name = 'LocalMetadataService'

    def _read_json(self, md_uri: str):
        """Read the metadata from the a json file"""
        if os.path.getsize(md_uri) > 0:
            with open(md_uri) as json_file:  
                return json.load(json_file)

    def _write_json(self, metadata: dict, md_uri: str):
        """Write the metadata to the a json file"""
        with open(md_uri, 'w') as outfile:
            json.dump(metadata, outfile, indent=4)     

    def read_rawdata(self, md_uri: str) -> RawDataContainer:
        if os.path.isfile(md_uri): 
            metadata = self._read_json(md_uri)
            container = RawDataContainer()
            container.type = metadata['origin']['type']
            container.name = metadata['common']['name']
            container.author = metadata['common']['author']
            container.date = metadata['common']['date']
            container.format = metadata['common']['format']
            # copy the url if absolute, append md_uri path otherwise
            container.uri = absolute_path(metadata['common']['url'], md_uri)  
            for key in metadata['tags']:
                container.tags[key] = metadata['tags'][key]    
            return container
        return RawDataContainer()    

    def write_rawdata(self, container: RawDataContainer, md_uri: str):
        metadata = dict()
        
        metadata['origin'] = dict()
        metadata['origin']['type'] = METADATA_TYPE_RAW()
        
        metadata['common'] = dict()
        metadata['common']['name'] = container.name
        metadata['common']['author'] = container.author
        metadata['common']['date'] = container.date
        metadata['common']['format'] = container.format
        metadata['common']['url'] = relative_path(container.uri, md_uri)

        metadata['tags'] = dict()
        for key in container.tags:
            metadata['tags'][key] = container.tags[key]

        self._write_json(metadata, md_uri)

    def read_processeddata(self, md_uri: str) -> ProcessedDataContainer:
        if os.path.isfile(md_uri): 
            metadata = self._read_json(md_uri)
            container = ProcessedDataContainer()
            container.name = metadata['common']['name']
            container.author = metadata['common']['author']
            container.date = metadata['common']['date']
            container.format = metadata['common']['format']
            container.uri = absolute_path(metadata['common']['url'], md_uri)
            # origin run
            container.run_uri = absolute_path(metadata['origin']['runurl'], md_uri)
            # origin input
            for input in metadata['origin']['inputs']:
                container.inputs.append(ProcessedDataInputContainer(input['name'], absolute_path(input['url'], md_uri), input['type']))
            # origin 
            if 'name' in metadata['origin']['output']:     
                container.output['name'] = metadata['origin']['output']["name"]
            if 'label' in metadata['origin']['output']:    
                container.output['label'] = metadata['origin']['output']['label']
                   
            return container
        return ProcessedDataContainer() 

    def write_processeddata(self, container: ProcessedDataContainer, md_uri: str):
        metadata = dict()
        # common
        metadata['common'] = dict()
        metadata['common']['name'] = container.name
        metadata['common']['author'] = container.author
        metadata['common']['date'] = container.date
        metadata['common']['format'] = container.format
        metadata['common']['url'] = relative_path(container.uri, md_uri)
        # origin type
        metadata['origin'] = dict()
        metadata['origin']['type'] = METADATA_TYPE_PROCESSED()
        # run url
        metadata['origin']['runurl'] = relative_path(container.run_uri, md_uri)
        # origin inputs
        metadata['origin']['inputs'] = list()
        for input in container.inputs:
            metadata['origin']['inputs'].append({'name':input.name,'url':relative_path(input.uri,md_uri), 'type':input.type})
        # origin ouput
        metadata['origin']['output'] = {'name':container.output['name'],'label':container.output['label']}
               
        self._write_json(metadata, md_uri)

    def read_rawdataset(self, md_uri: str) -> DataSetContainer: 
        if os.path.isfile(md_uri): 
            metadata = self._read_json(md_uri)
            container = DataSetContainer()
            container.name = metadata['name']
            for uri in metadata['urls']:
                container.uris.append(absolute_path(uri, md_uri))

            return container
        return DataSetContainer()  

    def write_rawdataset(self, container: DataSetContainer, md_uri: str):  
        metadata = dict()
        metadata['name'] = container.name
        metadata['urls'] = list()
        for uri in container.uris:
            metadata['urls'].append( relative_path(uri, md_uri ) )
        self._write_json(metadata, md_uri)      
    
    def read_processeddataset(self, md_uri: str) -> DataSetContainer: 
        if os.path.isfile(md_uri): 
            metadata = self._read_json(md_uri)
            container = DataSetContainer()
            container.name = metadata['name']
            for uri in metadata['urls']:
                container.uris.append(absolute_path(uri, md_uri))

            return container
        return DataSetContainer()        

    def write_processeddataset(self, container: DataSetContainer, md_uri: str):  
        metadata = dict()
        metadata['name'] = container.name
        metadata['urls'] = list()
        for uri in container.uris:
            metadata['urls'].append( relative_path(uri, md_uri ) )
        self._write_json(metadata, md_uri)     