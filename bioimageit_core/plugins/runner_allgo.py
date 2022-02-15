# -*- coding: utf-8 -*-
"""bioimageit_core Allgo process service.

This module implements a service to run a process
using the AllGo client API (allgo18.inria.fr). 

Classes
------- 
ProcessServiceProvider

"""

import os
import ntpath

import allgo as ag

from bioimageit_core.core.config import ConfigAccess
from bioimageit_core.core.utils import Observable
from bioimageit_core.processes.containers import ProcessContainer


class AllgoRunnerServiceBuilder:
    """Service builder for the runner service"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = AllgoRunnerService()
        return self._instance


class AllgoRunnerService(Observable):
    """Service for runner exec using AllGo client API"""

    def __init__(self):
        super().__init__()
        self.service_name = 'AllgoRunnerService'

    def set_up(self, process: ProcessContainer):
        """setup the runner

        Add here the code to initialize the runner

        Parameters
        ----------
        process
            Metadata of the process

        """
        pass

    def exec(self, process: ProcessContainer, args):
        """Execute a process

        Parameters
        ----------
        process
            Metadata of the process
        args
            list of arguments

        """
        token = None
        config = ConfigAccess.instance().config['runner']
        if 'token' in config:
            token = config['token']
        client = ag.Client(token)

        # exec the process
        params = ' '.join(args[1:])
        files = []
        for input_ in process.inputs:
            if input_.is_data:
                filename = ntpath.basename(input_.value)
                params = params.replace(input_.value, filename)
                files.append(input_.value)

        for output in process.outputs:
            if output.is_data:
                filename = ntpath.basename(output.value)
                params = params.replace(output.value, filename)

        # print('files:', files)
        # print('params:', params)

        try:
            out_dict = client.run_job(process.id, files=files, params=params)
        except ag.StatusError as e:
            print('API status Error:', e.status_code)
            print('API status Error:', e.msg)

        # print(out_dict)

        # get the outputs
        job_id = out_dict['id']
        for output in process.outputs:
            output_filename = ntpath.basename(output.value)
            output_dir = os.path.dirname(os.path.abspath(output.value))
            url = out_dict[str(job_id)][output_filename]
            filepath = client.download_file(file_url=url, outdir=output_dir,
                                            force=True)
            # print('out file downloaded at :', filepath)

    def tear_down(self, process: ProcessContainer):
        """tear down the runner

        Add here the code to down/clean the runner

        Parameters
        ----------
        process
            Metadata of the process

        """
        pass
