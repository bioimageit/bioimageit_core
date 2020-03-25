# -*- coding: utf-8 -*-
"""process module.

This module contains the Process class that allows to run a process on any
individual data. This class just run a data processing tools depending on the 
backend. It does not generate any metadata. This class purpose is mainly for 
writting data processing tools demo. If you need to process scientific data, please
use the Pipeline API.

Example
-------
    Here is an example of how to use Process with run on data
    loaded in python:

        >>> myprocess = Process('ndsafir')
        >>> imageio.imread('myimage.tif')
        >>> output_image = myprocess.run('i', input_image,
                'patch', patch,               
                'iter', iteration)

    Note that the Process class works only on data stored in files. Thus, if your
    data is loaded in python, the run funciton will save the data in temporary files 

    Another example using the 'exec' method to run the process of files

        >>> myprocess = Process('ndsafir') 
        >>> myprocess.run('i', 'myimage.tif',
                'patch', patch,               
                'iter', iteration,
                'o', 'denoised.tif') 

Classes
-------
Process
        
"""

import os
import shlex

from bioimagepy.config import ConfigAccess
from bioimagepy.runners.factory import runnerServices
from bioimagepy.process import Process

class Runner():
    def __init__(self, process:Process):
        self.process = process
        config = ConfigAccess.instance().config['runner']
        self.service = runnerServices.get(config['service'], **config) 

    def man(self):
        """Convenient method to print the process man"""
        self.process.man()

    def exec(self, *args):
        """Execute the process on files with the given arguments
        
        The inputs and outputs arguments have to be the path of the I/O data.
        args have to be pairs 'arg name, arg value' where arg name is the name
        of the parameter as given in the XML process file.

        Parameters
        ----------
        *args
            List of the parameters and I/O data given as pair 'arg name, arg value' 

        """
        # 1. check inputs
        for input_arg in self.process.metadata.inputs:
            if input_arg.name not in args and input_arg.type:
                print('Warning (Runner): cannot find the input ' + input_arg.name + ' will use the default value: ' + input_arg.default_value)
                input_arg.value = input_arg.default_value

        for output_arg in self.process.metadata.outputs:
            if output_arg.name not in args:
                print('Warning (Runner): cannot find the output ' + output_arg.name + ' will use the default value: ' + output_arg.default_value)
                output_arg.value = output_arg.default_value
        
        # 2. exec    
        # 2.1- get the parameters values
        for i in range(len(args)):
            arg = args[i]
            for input_arg in self.process.metadata.inputs:
                if input_arg.name == arg and input_arg.type:
                    input_arg.value = args[i+1]
            for output_arg in self.process.metadata.outputs:
                if output_arg.name == arg:    
                     output_arg.value = args[i+1] 

        # 2.2.1. build the command line   
        cmd = self.process.metadata.command   
        for input_arg in self.process.metadata.inputs:
            cmd = cmd.replace("${"+input_arg.name+"}", str(input_arg.value))
            input_arg_name_simple = input_arg.name.replace("-", "")
            cmd = cmd.replace("${"+input_arg_name_simple+"}", str(input_arg.value))
        for output_arg in self.process.metadata.outputs:
            cmd = cmd.replace("${"+output_arg.name+"}", str(output_arg.value))  

        # 2.2.2. replace the command variables
        cmd = self.replace_env_variables(cmd)
        cmd = " ".join(cmd.split())

        # 2.3. exec
        #print("cmd:", cmd)
        args = shlex.split(cmd)

        self.service.exec(self.process.metadata, args)

    def replace_env_variables(self, cmd) -> str:
        xml_root_path = os.path.dirname(os.path.abspath(self.process.uri))
        cmd_out = cmd.replace("$__tool_directory__", xml_root_path) 
        config = ConfigAccess.instance()
        if config.is_key('env'):
            for element in config.get('env'):
                cmd_out = cmd_out.replace("${"+element["name"]+"}", element["value"])
        return cmd_out          
