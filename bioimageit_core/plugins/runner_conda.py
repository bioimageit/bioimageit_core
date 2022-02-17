# -*- coding: utf-8 -*-
"""bioimageit_core local process service.

This module implements the local service for process
(Process class) execution. 

Classes
------- 
ProcessServiceProvider

"""
import os
import platform
import subprocess
from subprocess import Popen, PIPE, CalledProcessError

from bioimageit_core.core.observer import Observable
from bioimageit_core.core.config import ConfigAccess
from bioimageit_core.core.exceptions import ConfigError, RunnerExecError
from bioimageit_core.core.tools_containers import Tool


class CondaRunnerServiceBuilder:
    """Service builder for the runner service"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = CondaRunnerService()
        return self._instance


class CondaRunnerService(Observable):
    """Service for local runner exec

    To initialize the database, you need to set the xml_dirs from
    the configuration and then call initialize

    """

    def __init__(self):
        super().__init__()
        self.service_name = 'LocalRunnerService'
        conf_runner = ConfigAccess.instance().get('runner')
        if 'conda_dir' in conf_runner:
            self.conda_dir = ConfigAccess.instance().get('runner')['conda_dir']
        else:
            raise ConfigError('conda_dir is not set in the configuration file in runner section')

    def set_up(self, process: Tool):
        """setup the runner

        Add here the code to initialize the runner

        Parameters
        ----------
        process
            Metadata of the process

        """
        requirements = process.requirements[0]
        if requirements['origin'] == 'package' \
                and requirements['type'] == 'conda':
            package = requirements['package']
            env_name = process.id
            if 'env' in requirements:
                env_name = requirements['env']
            # get the list of envs
            envs_list = os.listdir(os.path.join(self.conda_dir, 'envs'))

            if env_name not in envs_list:
                # install: create env
                if platform.system() == 'Windows':
                    condaexe = os.path.join(self.conda_dir, 'condabin', 'conda.bat')
                    args_install = f"{condaexe} create -y -n {env_name} {package}"
                    print("install env cmd:", args_install)
                    subprocess.run(args_install, check=True)
                else:    
                    condash = os.path.join(self.conda_dir, 'etc', 'profile.d', 'conda.sh')
                    args_install = f". {condash} && conda create -y -n {env_name} {package}"
                    print("install env cmd:", args_install)
                    subprocess.run(args_install, shell=True, executable='/bin/bash',
                                   check=True)
            else:
                self.notify(f'{env_name} env already exists')
        else:
            raise RunnerExecError(f'Error: service conda cannot run the tool {process.fullname()}')

    def exec(self, process: Tool, args):
        """Execute a process

        Parameters
        ----------
        process
            Metadata of the process
        args
            list of arguments

        """
        requirements = process.requirements[0]
        env_name = process.id
        if 'env' in requirements:
            env_name = requirements['env']

        if platform.system() == 'Windows':
            condaexe = os.path.join(self.conda_dir, 'condabin', 'conda.bat')
            args_str = '"' + condaexe + '"' + ' activate '+env_name+' &&'
            for arg in args:
                args_str += ' ' + '"' + arg + '"'
            self.notify(f"Conda exec cmd: {args_str}")
            with Popen(args_str, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
                for b in p.stdout:
                    self.notify(b.strip())
            if p.returncode != 0:
                raise RunnerExecError(f'return code: {p.returncode}, for command: {p.args}')
        else:    
            condash = os.path.join(self.conda_dir, 'etc', 'profile.d', 'conda.sh')
            args_str = '. "' + condash + '"' + ' && conda activate '+env_name+' &&'
            for arg in args:
                args_str += ' ' + '"' + arg + '"'
            self.notify(f"Conda exec cmd: {args_str}")
            with Popen(args_str, shell=True, executable='/bin/bash', stdout=PIPE, bufsize=1,
                       universal_newlines=True) as p:
                for b in p.stdout:
                    self.notify(b.strip())
            if p.returncode != 0:
                raise RunnerExecError(f'return code: {p.returncode}, for command: {p.args}')

    def tear_down(self, process: Tool):
        """tear down the runner

        Add here the code to down/clean the runner

        Parameters
        ----------
        process
            Metadata of the process

        """
        pass
