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

from bioimageit_core.core.config import ConfigAccess
from bioimageit_core.core.observer import Observable
from bioimageit_core.containers.tools_containers import Tool
from bioimageit_core.core.exceptions import RunnerExecError


class DockerRunnerServiceBuilder:
    """Service builder for the runner service"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = DockerRunnerService()
        return self._instance


def extract_image_name(process: Tool):
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
        working_dir = config['working_dir'].replace('\\\\', '/').replace('\\',
                                                                         '/')
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

    def set_up(self, process: Tool):
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

    def exec(self, process: Tool, args):
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

        exec_args = ['docker', 'exec', image_name]
        for arg in args:
            arg = arg.replace('\\\\', '/').replace('\\', "/")
            print('arg =', arg)
            modified_arg = arg

            modified_arg = modified_arg.replace(working_dir, docker_data_dir)

            for input_ in process.inputs:
                # print('input ', input_.name, ' is data ', input_.is_data)
                if input_.is_data:
                    # print('input ', input_.name, ' goes to  modify_io_path with value ', input_.value)
                    modif_arg = self.modify_io_path(
                        arg, input_.value, working_dir, docker_data_dir
                    )
                    if modif_arg != '':
                        modified_arg = modif_arg
            for output in process.outputs:
                if output.is_data:
                    # print('output ', output.name, ' goes to  modify_io_path with value ', output.value)
                    modif_arg = self.modify_io_path(
                        arg, output.value, working_dir, docker_data_dir
                    )
                    if modif_arg != '':
                        modified_arg = modif_arg
            exec_args.append(modified_arg)
        print('exec cmd: ', exec_args)
        print()
        subprocess.run(exec_args)
        # subprocess.run(['docker', 'stop', image_name])

    def tear_down(self, process: Tool):
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

    @staticmethod
    def modify_io_path(
        arg: str, data_value: str, working_dir: str, docker_data_dir: str
    ):
        modified_arg = ''
        if arg == data_value or arg == data_value.replace('\\\\', '/').replace('\\', '/'):
            absolute_path = os.path.abspath(data_value).replace('\\\\', '/').replace('\\', '/')
            # print("absolute path=", absolute_path)
            # print("working_dir path=", working_dir)
            if working_dir in absolute_path:
                modified_arg = absolute_path.replace(working_dir,
                                                     docker_data_dir)
                modified_arg = modified_arg # .replace('\\\\', '/').replace('\\', '/')
                # print("modified_arg=", modified_arg)
            else:
                raise RunnerExecError(
                    "The docker runner can process only files "
                    "in the working_dir"
                )
        return modified_arg

    @staticmethod
    def relative_path(file: str, reference_file: str):
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

        common_part = ''
        for i in range(len(file)):
            common_part = reference_file[0:i]
            if common_part not in file:
                break

        last_separator = common_part.rfind(separator)

        short_reference_file = reference_file[last_separator + 1:]

        number_of_sub_folder = short_reference_file.count(separator)
        short_file = file[last_separator + 1:]
        for i in range(number_of_sub_folder):
            short_file = '..' + separator + short_file

        return short_file
