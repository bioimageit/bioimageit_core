# -*- coding: utf-8 -*-
"""BioImagePy Allgo process service.

This module implements a service to run a process
using the AllGo client API (allgo18.inria.fr). 

Classes
------- 
ProcessServiceProvider

"""

import os
import ntpath

import allgo as ag

from bioimagepy.config import ConfigAccess
from bioimagepy.core.utils import Observable
from bioimagepy.processes.containers import ProcessContainer
from bioimagepy.runners.exceptions import RunnerExecError


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
        for input in process.inputs:
            if input.is_data:
                filename = ntpath.basename(input.value)
                params = params.replace(input.value, filename)
                files.append(input.value)

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
            filepath = client.download_file(file_url=url, outdir=output_dir, force=True)
            # print('out file downloaded at :', filepath)
