# -*- coding: utf-8 -*-
"""BioImagePy process service provider.

This module implement the process service provider

Classes
------- 
MetadataServiceProvider

"""

from bioimagepy.core.factory import ObjectFactory
from bioimagepy.processes.service_local import LocalProcessServiceBuilder

class ProcessServiceProvider(ObjectFactory):
    def get(self, service_id, **kwargs):
        return self.create(service_id, **kwargs)


processServices = ProcessServiceProvider()
processServices.register_builder('LOCAL', LocalProcessServiceBuilder())
#metadataServices.register_builder('SINGULARITY', SingularityProcessServiceBuilder())