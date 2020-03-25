# -*- coding: utf-8 -*-
"""BioImagePy local process service.

This module implements the local service for process
(Process class) execution. 

Classes
------- 
ProcessServiceProvider

"""

import os.path
from spython.main import Client

from bioimagepy.config import ConfigAccess
from bioimagepy.processes.containers import ProcessContainer
from bioimagepy.runners.exceptions import RunnerExecError

class SingularityRunnerServiceBuilder:
    """Service builder for the runner service"""
    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = SingularityRunnerService()
        return self._instance

class SingularityRunnerService:
    """Service for local runner exec
    
    To initialize the database, you need to set the xml_dirs from 
    the configuration and then call initialize
    
    """
    def __init__(self):
        self.service_name = 'SingularityRunnerService'

    def exec(self, process:ProcessContainer, args):
        """Execute a process

        Parameters
        ----------
        process
            Metadata of the process
        args
            list of arguments    

        """
        if not process.container['type'] == 'singularity':
            raise RunnerExecError("The process " + process.name + " is not compatible with Singularity" )    

        image_uri = replace_env_variables(process, process.container['uri'])
        print("run singularity container:", image_uri)
        puller = Client.execute(image_uri, args)    
        # TODO add puller to log via observer
        for line in puller:
            print(line)

def replace_env_variables(process, cmd) -> str:
    xml_root_path = os.path.dirname(os.path.abspath(process.uri))
    cmd_out = cmd.replace("$__tool_directory__", xml_root_path) 
    config = ConfigAccess.instance()
    if config.is_key('env'):
        for element in config.get('env'):
            cmd_out = cmd_out.replace("${"+element["name"]+"}", element["value"])
    return cmd_out                 