# -*- coding: utf-8 -*-
"""BioImagePy metadata service provider.

This module implement the metadata service provider

Classes
------- 
MetadataServiceProvider

"""
import importlib
import pkgutil

from bioimageit_core.core.factory import ObjectFactory
from bioimageit_core.plugins.data_local import LocalMetadataServiceBuilder

class MetadataServiceProvider(ObjectFactory):
    def get(self, service_id, **kwargs):
        print('get service:', service_id)
        return self.create(service_id, **kwargs)


exclude_list = ['bioimageit_core', 'bioimageit_gui', 'bioimageit_formats', 'bioimageit_framework', 'bioimageit_viewer']
discovered_plugins = {
    name: importlib.import_module(name)
    for finder, name, ispkg
    in pkgutil.iter_modules()
    if name.startswith('bioimageit_') and name not in exclude_list
}

metadataServices = MetadataServiceProvider()
metadataServices.register_builder('LOCAL', LocalMetadataServiceBuilder())

for name, module in discovered_plugins.items():
    mod = __import__(name)
    if mod.plugin_info['type'] == 'data':
        metadataServices.register_builder(mod.plugin_info['name'], getattr(mod, mod.plugin_info['builder'])())
