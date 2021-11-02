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

from bioimageit_core.core.utils import Observable
from bioimageit_core.config import ConfigAccess
from bioimageit_core.processes.containers import ProcessContainer


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
        self.conda_dir = ConfigAccess.instance().get('runner')['conda_dir']
        print(self.conda_dir)

    def set_up(self, process: ProcessContainer):
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
            #init_cmd = requirements['init']

            # install env if not exists
            #if platform.system() == 'Windows':
            #    args_exists = f"{self.condash} env list"
            #    print("exists env cmd:", args_exists)
            #    proc = subprocess.run(args_exists, check=True, stdout=subprocess.PIPE)
            #else:    
            #    args_exists = f". {self.condash} && conda env list"
            #    print("exists env cmd:", args_exists)
            #    proc = subprocess.run(args_exists, shell=True, executable='/bin/bash',
            #                          check=True, stdout=subprocess.PIPE)

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
                print(env_name + ' env already exists')
        else:
            print('Error: service conda cannot run this process')

    def exec(self, process: ProcessContainer, args):
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

        #args_list = [self.condash, 'activate', env_name, '&&'] + args
        if platform.system() == 'Windows':
            condaexe = os.path.join(self.conda_dir, 'condabin', 'conda.bat')
            args_str = '"' + condaexe + '"' + 'activate '+env_name+' &&'
            for arg in args:
                args_str += ' ' + '"' + arg + '"'
            print("final exec cmd:", args_str)
            subprocess.run(args_str, check=True)
        else:    
            condash = os.path.join(self.conda_dir, 'etc', 'profile.d', 'conda.sh')
            args_str = '. "' + condash + '"' + ' && conda activate '+env_name+' &&'
            for arg in args:
                args_str += ' ' + '"' + arg + '"'
            print("final exec cmd:", args_str)
            subprocess.run(args_str, shell=True, executable='/bin/bash',
                           check=True)

    def tear_down(self, process: ProcessContainer):
        """tear down the runner

        Add here the code to down/clean the runner

        Parameters
        ----------
        process
            Metadata of the process

        """
        pass
