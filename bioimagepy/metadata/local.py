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
import json

from bioimagepy.metadata.containers import METADATA_TYPE_RAW, RawDataContainer


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

        import os.path
        if os.path.isfile(md_uri): 
            metadata = self._read_json(md_uri)
            container = RawDataContainer()
            container.type = metadata['origin']['type']
            container.name = metadata['common']['name']
            container.author = metadata['common']['author']
            container.date = metadata['common']['date']
            container.format = metadata['common']['format']
            container.uri = metadata['common']['url']
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
        metadata['common']['url'] = container.uri

        metadata['tags'] = dict()
        for key in container.tags:
            metadata['tags'][key] = container.tags[key]

        self._write_json(metadata, md_uri)

