# -*- coding: utf-8 -*-
"""bioimageit_core local process service.

This module implements the local service for process
(Process class) execution. 

Classes
------- 
ProcessServiceProvider

"""

import subprocess

from bioimageit_core.core.observer import Observable
from bioimageit_core.core.tools_containers import Tool


class LocalRunnerServiceBuilder:
    """Service builder for the runner service"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = LocalRunnerService()
        return self._instance


class LocalRunnerService(Observable):
    """Service for local runner exec

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
        tool
            Metadata of the tool

        """
        pass

    def exec(self, process: Tool, args):
        """Execute a process

        Parameters
        ----------
        process
            Metadata of the process
        args
            list of arguments

        """
        subprocess.run(args)

    def tear_down(self, process: Tool):
        """tear down the runner

        Add here the code to down/clean the runner

        Parameters
        ----------
        process
            Metadata of the process

        """
        pass
