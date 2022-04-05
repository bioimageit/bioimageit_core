# -*- coding: utf-8 -*-
"""BioImagePy metadata service provider.

This module implement the metadata service provider

Classes
------- 
MetadataServiceProvider

"""

from bioimageit_core.core.factory import ObjectFactory
from bioimageit_core.plugins.data_local import LocalMetadataServiceBuilder

use_omero = False
try:
    from bioimageit_core.plugins.data_omero import OmeroMetadataServiceBuilder
    use_omero = True
except ImportError as e:
    print('Warning: cannot find the Omero toolbox')




class MetadataServiceProvider(ObjectFactory):
    def get(self, service_id, **kwargs):
        return self.create(service_id, **kwargs)


metadataServices = MetadataServiceProvider()
metadataServices.register_builder('LOCAL', LocalMetadataServiceBuilder())
if use_omero:
    metadataServices.register_builder('OMERO', OmeroMetadataServiceBuilder())
