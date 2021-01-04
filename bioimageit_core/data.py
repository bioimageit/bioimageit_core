# -*- coding: utf-8 -*-
"""BioImagePy Data definitions.

This module contains classes that to manimpulate scientific
data metadata using RawData and ProcessedData

Classes
-------
Data
RawData
ProcessedData

"""

from bioimageit_core.config import ConfigAccess
from bioimageit_core.metadata.containers import (METADATA_TYPE_RAW,
                                                 RawDataContainer,
                                                 ProcessedDataContainer,
                                                 ProcessedDataInputContainer,
                                                 SearchContainer)
from bioimageit_core.metadata.exceptions import MetadataServiceError
from bioimageit_core.metadata.factory import metadataServices


class RawData:
    """interact with raw data metadata

    RawData allows to read/write and manipulate the metadata
    of a raw data.

    Parameters
    ----------
    md_uri
        URI of the metadata in the database or file system
        depending on backend

    Attributes
    ----------
    metadata
        Container of the metadata

    """

    def __init__(self, md_uri: str):
        self.md_uri = md_uri
        self.metadata = None  # RawDataContainer()
        config = ConfigAccess.instance().config['metadata']
        self.service = metadataServices.get(config["service"], **config)
        try:
            self.read()
        except MetadataServiceError:
            self.metadata = RawDataContainer()

    def read(self):
        """Read the metadata from database

        The data base connection is managed by the configuration
        object

        """
        self.metadata = self.service.read_rawdata(self.md_uri)

    def write(self):
        """Write the metadata to database

        The data base connection is managed by the configuration
        object

        """
        self.service.write_rawdata(self.metadata, self.md_uri)

    def to_search_container(self) -> SearchContainer:
        """convert to SearchContainer

        Create a serch container from the data metadata

        """
        info = SearchContainer()
        info.data['name'] = self.metadata.name
        info.data["uri"] = self.md_uri
        info.data['tags'] = self.metadata.tags
        return info

    def set_tag(self, tag_key: str, tag_value: str):
        """Set a tag to the data

        If the tag key does not exists for this data, it is
        created. If the tag key exists the value is changed

        Parameters
        ----------
        tag_key
            Key of the tag
        tag_value
            Value of the tag

        """
        self.metadata.tags[tag_key] = tag_value
        self.service.write_rawdata(self.metadata, self.md_uri)

    def tag(self, tag_key: str):
        """get a tag value from key

        get a tag in the metadata. It returns and empty
        string if the tag does not exists

        Parameters
        ----------
        tag_key
            Key of the tag to get

        Returns
        -------
        The value of the tag or an empty string is not exists

        """
        if tag_key in self.metadata.tags:
            return self.metadata.tags[tag_key]
        return ''

    def display(self):
        """Display metadata in console"""
        print(self.metadata.serialize())


class ProcessedData:
    """Class that store a raw data metadata

    RawData allows to read/write and manipulate the metadata
    of a raw data.

    Parameters
    ----------
    md_uri
        URI of the metadata in the database or file system
        depending on backend

    Attributes
    ----------
    metadata
        Container of the metadata

    """

    def __init__(self, md_uri: str = ''):
        self.md_uri = md_uri
        self.metadata = None  # ProcessedDataContainer()
        config = ConfigAccess.instance().config['metadata']
        self.service = metadataServices.get(config["service"], **config)
        try:
            self.read()
        except MetadataServiceError:
            self.metadata = ProcessedDataContainer()

    def read(self):
        """Read the metadata from database

        The data base connection is managed by the configuration
        object

        """
        self.metadata = self.service.read_processeddata(self.md_uri)
        pass

    def write(self):
        """Write the metadata to database

        The data base connection is managed by the configuration
        object

        """
        self.service.write_processeddata(self.metadata, self.md_uri)
        pass

    def display(self):
        """Display metadata in console"""
        print(self.metadata.serialize())

    def add_input(self, name: str, uri: str, type_: str):
        self.metadata.inputs.append(ProcessedDataInputContainer(name,
                                                                uri,
                                                                type_))

    def set_output(self, name: str, label: str):
        self.metadata.output['name'] = name
        self.metadata.output['label'] = label

    def get_parent(self):
        """Get the metadata of the parent data.

        The parent data can be a RawData or a ProcessedData
        depending on the process chain

        Returns
        -------
        parent
            Parent data (RawData or ProcessedData)

        """

        if len(self.metadata.inputs) > 0:

            if self.metadata.inputs[0].type == METADATA_TYPE_RAW():
                return RawData(self.metadata.inputs[0].uri)
            else:
                return ProcessedData(self.metadata.inputs[0].uri)
        return None

    def get_origin(self) -> RawData:
        """Get the first metadata of the parent data.

        The origin data is a RawData. It is the first data that have
        been seen by bioimageit_core

        Returns
        -------
        the origin data in a RawData object

        """
        return processed_data_origin(self)

    def to_search_container(self) -> SearchContainer:
        """convert to SearchContainer

        Create a search container from the data metadata

        """
        container = None
        try:
            origin = self.get_origin()
            if origin is not None:
                container = origin.to_search_container()
            else:
                container = SearchContainer()
        except MetadataServiceError:
            container = SearchContainer()
        container.data['name'] = self.metadata.name
        container.data['uri'] = self.md_uri
        return container


# queries
def processed_data_origin(processed_data: ProcessedData):
    if len(processed_data.metadata.inputs) > 0:
        if processed_data.metadata.inputs[0].type == METADATA_TYPE_RAW():
            return RawData(processed_data.metadata.inputs[0].uri)
        else:
            return processed_data_origin(
                ProcessedData(processed_data.metadata.inputs[0].uri)
            )
