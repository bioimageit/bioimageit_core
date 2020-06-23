# -*- coding: utf-8 -*-
"""BioImagePy docker process service.

This module implements a service to run process in
using Docker. 

Classes
------- 
ProcessServiceProvider

"""

import os
import subprocess
import ntpath

from bioimagepy.config import ConfigAccess
from bioimagepy.core.utils import Observable
from bioimagepy.processes.containers import ProcessContainer
from bioimagepy.runners.exceptions import RunnerExecError

class DockerRunnerServiceBuilder:
    """Service builder for the runner service"""
    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = DockerRunnerService()
        return self._instance

class DockerRunnerService(Observable):
    """Service for docker runner exec
    
    To initialize the database, you need to set the xml_dirs from 
    the configuration and then call initialize
    
    """
    def __init__(self):
        super().__init__()
        self.service_name = 'LocalRunnerService'

    def exec(self, process:ProcessContainer, args):
        """Execute a process

        Parameters
        ----------
        process
            Metadata of the process
        args
            list of arguments    

        """

        # check container type
        if process.container()['type'] != 'docker':
            raise RunnerExecError("The process " + process.name + " is not compatible with Docker" )  
        image_uri = process.container()['uri']    

        # get a name for the image
        image_name = ''
        image_split = image_uri.split(':')
        if len(image_split) == 2:
            image_name = image_split[0].split('/')[-1]
        else:
            image_name = process.name.replace(' ', '')

        # pull the docker image
        
        pull_args = ['docker',  'pull', image_uri]
        #print('pull cmd: ', pull_args)
        #print()  
        subprocess.run(pull_args)
        
        # run the docker image (to create container)
        docker_data_dir = '/app/data/'
        working_dir = ''
        config = ConfigAccess.instance().config['runner']
        if 'working_dir' in config:
            working_dir = config['working_dir'] 
        else:
            raise RunnerExecError("The docker runner need a  working_dir. Please setup working_dir in your config file" )      

        run_args = ['docker', 'run', '--name', image_name, '-v', working_dir + ':' + docker_data_dir, '-it', '-d', image_uri]
        #print('run cmd: ', run_args) 
        #print()     
        subprocess.run(run_args)

        # exec the command
        exec_args = ['docker', 'exec', '-it', image_name]
        for arg in args:
            modified_arg = arg
            for input in process.inputs:
                if input.is_data:
                    modif_arg = self.modify_io_path(arg, input.value, working_dir, docker_data_dir) 
                    if modif_arg != '':
                        modified_arg = modif_arg       
            for output in process.outputs:
                if output.is_data:
                    modif_arg = self.modify_io_path(arg, output.value, working_dir, docker_data_dir) 
                    if modif_arg != '':
                        modified_arg = modif_arg    
            exec_args.append(modified_arg)
        #print('exec cmd: ', exec_args) 
        #print()       
        subprocess.run(exec_args)


    def modify_io_path(self, arg:str, data_value:str, working_dir:str, docker_data_dir:str ):
        modified_arg = ''
        if arg == data_value:
            absolute_path = os.path.abspath(data_value)
            if working_dir in absolute_path:
                modified_arg = absolute_path.replace(working_dir, docker_data_dir)
            else:
                raise RunnerExecError("The docker runner can process only files in the working_dir")
        return modified_arg              

    def relative_path(self, file:str, reference_file:str):
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