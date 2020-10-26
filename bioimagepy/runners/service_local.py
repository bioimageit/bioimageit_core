# -*- coding: utf-8 -*-
"""BioImagePy local process service.

This module implements the local service for process
(Process class) execution. 

Classes
------- 
ProcessServiceProvider

"""

import subprocess

from bioimagepy.core.utils import Observable
from bioimagepy.processes.containers import ProcessContainer
from bioimagepy.runners.exceptions import RunnerExecError


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

    def exec(self, process: ProcessContainer, args):
        """Execute a process

        Parameters
        ----------
        process
            Metadata of the process
        args
            list of arguments

        """
        subprocess.run(args)
