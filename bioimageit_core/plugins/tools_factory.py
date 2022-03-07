# -*- coding: utf-8 -*-
"""BioImagePy process service provider.

This module implement the process service provider

Classes
------- 
MetadataServiceProvider

"""

from bioimageit_core.core.factory import ObjectFactory
from bioimageit_core.plugins.tools_local import LocalToolsServiceBuilder


class ToolsServiceProvider(ObjectFactory):
    def get(self, service_id, **kwargs):
        return self.create(service_id, **kwargs)


toolsServices = ToolsServiceProvider()
toolsServices.register_builder('LOCAL', LocalToolsServiceBuilder())
