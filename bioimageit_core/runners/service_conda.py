# -*- coding: utf-8 -*-
"""bioimageit_core local process service.

This module implements the local service for process
(Process class) execution. 

Classes
------- 
ProcessServiceProvider

"""
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
        self.condash = ConfigAccess.instance().get('runner')['condash']
        print(self.condash)

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
            args_exists = [self.condash, 'env', 'list']
            print("exists env cmd:", args_exists)
            if platform.system() == 'Windows':
                proc = subprocess.run(args_exists, check=True, stdout=subprocess.PIPE)
            else:    
                proc = subprocess.run(args_exists, shell=True, executable='/bin/bash',
                                      check=True, stdout=subprocess.PIPE)

            if env_name not in str(proc.stdout):
                # install: create env
                package_list = package.split()
                args_install = [self.condash, 'create', '-y', '-n', env_name] + package_list
                print("install env cmd:", args_install)

                if platform.system() == 'Windows':
                    subprocess.run(args_install, check=True)
                else:    
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

        args_list = [self.condash, 'activate', env_name, '&&'] + args

        if platform.system() == 'Windows':
            subprocess.run(args_list, check=True)
        else:    
            subprocess.run(args_list, shell=True, executable='/bin/bash',
                           check=True)

        #args_str = '"' + self.condash + '"' + ' activate '+env_name+' &&'
        #for arg in args:
        #    args_str += ' ' + '"' + arg + '"'
        #print("final exec cmd:", args_str)
        #subprocess.run(args_str, check=True)

    def tear_down(self, process: ProcessContainer):
        """tear down the runner

        Add here the code to down/clean the runner

        Parameters
        ----------
        process
            Metadata of the process

        """
        pass
