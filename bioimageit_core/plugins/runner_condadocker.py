# -*- coding: utf-8 -*-
"""bioimageit_core local process service.

This module implements the local service for process
(Process class) execution. 

Classes
------- 
ProcessServiceProvider

"""
from bioimageit_core.core.observer import Observable
from bioimageit_core.core.tools_containers import Tool

from bioimageit_core.plugins.runner_conda import CondaRunnerService
from bioimageit_core.plugins.runner_docker import DockerRunnerService


class CondaDockerRunnerServiceBuilder:
    """Service builder for the runner service"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = CondaDockerRunnerService()
        return self._instance


class CondaDockerRunnerService(Observable):
    """Service for runner that switch between conda and docker wrt the wrapper

    To initialize the database, you need to set the xml_dirs from
    the configuration and then call initialize

    """

    def __init__(self):
        super().__init__()
        self.service_name = 'LocalRunnerService'

    @staticmethod
    def set_up(process: Tool):
        """setup the runner

        Add here the code to initialize the runner

        Parameters
        ----------
        process
            Metadata of the process

        """
        requirements = process.requirements[0]
        print("Conda Docker runner requirements=", requirements)
        if requirements['origin'] == 'package' and \
                requirements['type'] == 'conda':
            print('CondaDockerRunnerService: run conda')
            service = CondaRunnerService()
            service.set_up(process)
        elif requirements['origin'] == 'container' and \
                requirements['type'] == 'docker':
            print('CondaDockerRunnerService: run docker')
            service = DockerRunnerService()
            service.set_up(process)
        else:
            print('CondaDockerRunnerService: cannot find the runner')

    @staticmethod
    def exec(process: Tool, args):
        """Execute a process

        Parameters
        ----------
        process
            Metadata of the process
        args
            list of arguments

        """
        requirements = process.requirements[0]
        if requirements['origin'] == 'package' and \
                requirements['type'] == 'conda':
            service = CondaRunnerService()
            service.exec(process, args)
        elif requirements['origin'] == 'container' and \
                requirements['type'] == 'docker':
            service = DockerRunnerService()
            service.exec(process, args)

    @staticmethod
    def tear_down(process: Tool):
        """tear down the runner

        Add here the code to down/clean the runner

        Parameters
        ----------
        process
            Metadata of the process

        """
        requirements = process.requirements[0]
        if requirements['origin'] == 'package' and \
                requirements['type'] == 'conda':
            service = CondaRunnerService()
            service.tear_down(process)
        elif requirements['origin'] == 'container' and \
                requirements['type'] == 'docker':
            service = DockerRunnerService()
            service.tear_down(process)
