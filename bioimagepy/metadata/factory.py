# -*- coding: utf-8 -*-
"""BioImagePy metadata service provider.

This module implement the metadata service provider

Classes
------- 
MetadataServiceProvider

"""

from bioimagepy.core.factory import ObjectFactory
from bioimagepy.metadata.service_local import LocalMetadataServiceBuilder

class MetadataServiceProvider(ObjectFactory):
    def get(self, service_id, **kwargs):
        return self.create(service_id, **kwargs)


metadataServices = MetadataServiceProvider()
metadataServices.register_builder('LOCAL', LocalMetadataServiceBuilder())
#metadataServices.register_builder('OMERO', OmeroMetadataServiceBuilder())