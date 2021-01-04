# -*- coding: utf-8 -*-
"""bioimageit_core docker process service.

This module implements a service to run process in
using Docker. 

Classes
------- 
ProcessServiceProvider

"""

import os
import subprocess

from bioimageit_core.config import ConfigAccess
from bioimageit_core.core.utils import Observable
from bioimageit_core.processes.containers import ProcessContainer
from bioimageit_core.runners.exceptions import RunnerExecError


class DockerRunnerServiceBuilder:
    """Service builder for the runner service"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = DockerRunnerService()
        return self._instance


def extract_image_name(process: ProcessContainer):
    image_uri = process.container()['uri']
    image_name = ''
    image_split = image_uri.split(':')
    if len(image_split) == 2:
        image_name = image_split[0].split('/')[-1]
    else:
        image_name = process.name.replace(' ', '')
    return image_name


def get_docker_working_dir():
    working_dir = ''
    config = ConfigAccess.instance().config['runner']
    if 'working_dir' in config:
        working_dir = config['working_dir']
    else:
        raise RunnerExecError(
            "The docker runner need a  working_dir. "
            "Please setup working_dir in your config file"
        )
    return working_dir


class DockerRunnerService(Observable):
    """Service for docker runner exec

    To initialize the database, you need to set the xml_dirs from
    the configuration and then call initialize

    """

    def __init__(self):
        super().__init__()
        self.service_name = 'LocalRunnerService'

    def set_up(self, process: ProcessContainer):
        """setup the runner

        Add here the code to initialize the runner

        Parameters
        ----------
        process
            Metadata of the process

        """
        # check container type
        if process.container()['type'] != 'docker':
            raise RunnerExecError(
                "The process " + process.name + " is not compatible with Docker"
            )
        image_uri = process.container()['uri']

        # pull the docker image
        pull_args = ['docker', 'pull', image_uri]
        # print('pull cmd: ', pull_args)
        # print()
        subprocess.run(pull_args)

        # run the docker image (to create container)
        docker_data_dir = '/app/data/'
        working_dir = get_docker_working_dir()

        # get a name for the image
        image_uri = process.container()['uri']
        image_name = extract_image_name(process)

        run_args = [
            'docker',
            'run',
            '--name',
            image_name,
            '-v',
            working_dir + ':' + docker_data_dir,
            '-it',
            '-d',
            image_uri,
        ]
        print('run cmd: ', run_args)
        print()
        subprocess.run(run_args)

    def exec(self, process: ProcessContainer, args):
        """Execute a process

        Parameters
        ----------
        process
            Metadata of the process
        args
            list of arguments

        """

        # get a name for the image
        image_name = extract_image_name(process)
        docker_data_dir = '/app/data/'
        working_dir = get_docker_working_dir()

        # exec the command
        exec_args = ['docker', 'exec', '-it', image_name]
        for arg in args:
            modified_arg = arg
            for input in process.inputs:
                if input.is_data:
                    modif_arg = self.modify_io_path(
                        arg, input.value, working_dir, docker_data_dir
                    )
                    if modif_arg != '':
                        modified_arg = modif_arg
            for output in process.outputs:
                if output.is_data:
                    modif_arg = self.modify_io_path(
                        arg, output.value, working_dir, docker_data_dir
                    )
                    if modif_arg != '':
                        modified_arg = modif_arg
            exec_args.append(modified_arg)
        print('exec cmd: ', exec_args)
        print()
        subprocess.run(exec_args)

    def tear_down(self, process: ProcessContainer):
        """tear down the runner

        Add here the code to down/clean the runner

        Parameters
        ----------
        process
            Metadata of the process

        """
        image_name = extract_image_name(process)

        # stop container
        stop_args = ['docker', 'stop', image_name]
        print('stop cmd: ', stop_args)
        print()
        subprocess.run(stop_args)

        # remove container
        rm_args = ['docker', 'rm', image_name]
        print('rm cmd: ', rm_args)
        print()
        subprocess.run(rm_args)

    def modify_io_path(
        self, arg: str, data_value: str, working_dir: str, docker_data_dir: str
    ):
        modified_arg = ''
        if arg == data_value:
            absolute_path = os.path.abspath(data_value)
            if working_dir in absolute_path:
                modified_arg = absolute_path.replace(working_dir,
                                                     docker_data_dir)
            else:
                raise RunnerExecError(
                    "The docker runner can process only files "
                    "in the working_dir"
                )
        return modified_arg

    def relative_path(self, file: str, reference_file: str):
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
        file = file.replace(separator + separator, separator)
        reference_file = reference_file.replace(separator + separator,
                                                separator)

        for i in range(len(file)):
            common_part = reference_file[0:i]
            if common_part not in file:
                break

        last_separator = common_part.rfind(separator)

        shortreference_file = reference_file[last_separator + 1:]

        numberOfSubFolder = shortreference_file.count(separator)
        shortfile = file[last_separator + 1:]
        for i in range(numberOfSubFolder):
            shortfile = '..' + separator + shortfile

        return shortfile
