# -*- coding: utf-8 -*-
"""bioimageit_core Run definitions.

This module contains classes that to manipulate a run
metadata

Classes
------- 
Run

"""

from bioimageit_core.core.config import ConfigAccess
from bioimageit_core.metadata.factory import metadataServices


class Run:
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

    def __init__(self, md_uri: str = ''):
        self.md_uri = md_uri
        self.metadata = None  # RunContainer()
        config = ConfigAccess.instance().config['metadata']
        self.service = metadataServices.get(config["service"], **config)
        self.read()

    def read(self):
        """Read the metadata from database

        The data base connection is managed by the configuration
        object

        """
        self.metadata = self.service.read_run(self.md_uri)

    def write(self):
        """Write the metadata to database

        The data base connection is managed by the configuration
        object

        """
        self.service.write_run(self.metadata, self.md_uri)
