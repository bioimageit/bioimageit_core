# -*- coding: utf-8 -*-
"""process module.

This module contains the Process class that allows to run a process on any
individual data. This class just run a data processing tools depending on the 
backend. It does not generate any metadata. This class purpose is mainly for 
writting data processing tools demo. If you need to process scientific data, please
use the Pipeline API.

Example
-------
    Runner can be used to run a process on a single data with the exec method:
        >>> myrunner = Runner(ProcessAccess().get('ndsafir_v1.0.0') 
        >>> myrunner.exec('i', 'myimage.tif',
                'patch', patch,               
                'iter', iteration,
                'o', 'denoised.tif') 

    If you want the outputs to be automatically names you can use
        >>> myrunner = Runner(ProcessAccess().get('ndsafir_v1.0.0') 
        >>> myrunner.add_input('i', 'myimage.tif')
        >>> myrunner.set_parameters('patch', patch,               
                                    'iter', iteration)
        >>> myrunner.set_output('/my/output/directory')  
        >>> myrunner.exec()                                  

    Runner can also run on a batch of data:

        >>> myrunner = Runner(ProcessAccess().get('ndsafir_v1.0.0'))
        >>> myrunner.add_inputs('i', '/my/input/directory/', '\.tif$')
        >>> myrunner.set_parameters('patch', patch,               
                                    'iter', iteration)
        >>> myrunner.set_output('/my/output/directory')
        >>> myrunner.exec()                                        

Classes
-------
Process
        
"""

import os
import shlex

from bioimagepy.core.utils import Observable
from bioimagepy.config import ConfigAccess
from bioimagepy.runners.factory import runnerServices
from bioimagepy.metadata.factory import metadataServices
from bioimagepy.process import Process
from bioimagepy.runners.exceptions import RunnerExecError


class Runner(Observable):
    def __init__(self, process: Process):
        super().__init__()
        self.process = process
        config = ConfigAccess.instance().config['runner']
        self.service = runnerServices.get(config['service'], **config)
        self.metadataservice = metadataServices.get(
            ConfigAccess.instance().config['metadata']['service'], **config
        )
        self._inputs = (
            []
        )  # list of {"name": "i", "uri": "/my/directory/", "filter": "\.tif$"" }
        self._parameters = []  # [key1, value1, key2, value1, ...]
        self._output = ''  # output uri (/my/output/folder)
        self._mode = ''
        self.output_uris = []  # list of generated outputs

    def man(self):
        """Convenient method to print the process man"""
        self.process.man()

    def add_inputs(self, name: str, uri: str, filter: str):
        self._mode = 'list'
        self._inputs.append({"name": name, "uri": uri, "filter": filter})

    def add_input(self, name: str, uri: str):
        self._mode = 'single'
        self._inputs.append({"name": name, "uri": uri})

    def set_parameters(self, *args):
        self._parameters = args

    def set_output(self, uri: str):
        self._output = uri

    def exec(self, *args):
        """Execute the process

        If the arguments list is empty it exec on the data list defined with
        the setters add_inputs

        Parameters
        ----------
        *args
            List of the parameters and I/O data given as pair 'arg name, arg value'

        """

        if self.observers_count() > self.service.observers_count():
            for observer in self._observers:
                self.service.add_observer(observer)
        # print("runner exec with len(args)", len(args))
        # print("parameters:", self._parameters)
        self.notify_observers(0, "Started")
        if len(args) == 0:
            self._exec_list()
        else:
            self._exec_file(*args)
        self.notify_observers(100, "Done")

    def _exec_list(self):

        # merge input
        inputs = {}

        data_count = 0
        if self._mode == 'list':
            iter = -1
            for input in self._inputs:
                iter = iter + 1

                uris = self.metadataservice.query_rep(input['uri'], input['filter'])
                if iter == 0:
                    data_count = len(uris)
                else:
                    if len(uris) != data_count:
                        raise RunnerExecError(
                            "Inputs data number are not equal for all input"
                        )
                inputs[input['name']] = uris
        elif self._mode == 'single':
            data_count = 1
            for input in self._inputs:
                inputs[input['name']] = [input['uri']]

        self.output_uris = []
        for i in range(data_count):

            self.notify_observers(
                100 * (i / data_count),
                "Process data " + str(i + 1) + "/" + str(data_count),
            )
            args = []

            # create the input
            for key in inputs:
                args.append(key)
                args.append(inputs[key][i])

            # create output names
            out_list = []
            for output in self.process.metadata.outputs:

                # output metadata
                output_uri = self.metadataservice.create_output_uri(
                    self._output, output.name, output.type, args[1]
                )

                # args
                args.append(output.name)
                args.append(output_uri)

                # keep output in memory with a dict
                out_list.append(
                    {'name': output.name, 'uri': output_uri, 'format': output.type}
                )

            self.output_uris.append(out_list)

            # append parameters
            for param in self._parameters:
                args.append(param)

            # exec
            # print('args:', args)
            self._exec_file(*args)

    def _exec_file(self, *args):
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
                print(
                    'Warning (Runner): cannot find the input: '
                    + input_arg.name
                    + ' will use the default value: '
                    + input_arg.default_value
                )
                input_arg.value = input_arg.default_value

        for output_arg in self.process.metadata.outputs:
            if output_arg.name not in args:
                print(
                    'Warning (Runner): cannot find the output: '
                    + output_arg.name
                    + ' will use the default value: '
                    + output_arg.default_value
                )
                output_arg.value = output_arg.default_value

        # 2. exec
        # 2.1- get the parameters values
        for i in range(len(args)):
            arg = args[i]
            for input_arg in self.process.metadata.inputs:
                if input_arg.name == arg and input_arg.type:
                    input_arg.value = args[i + 1]
            for output_arg in self.process.metadata.outputs:
                if output_arg.name == arg:
                    output_arg.value = args[i + 1]

        # 2.2.1. build the command line
        cmd = self.process.metadata.command
        for input_arg in self.process.metadata.inputs:
            cmd = cmd.replace("${" + input_arg.name + "}", str(input_arg.value))
            input_arg_name_simple = input_arg.name.replace("-", "")
            cmd = cmd.replace("${" + input_arg_name_simple + "}", str(input_arg.value))
        for output_arg in self.process.metadata.outputs:
            cmd = cmd.replace("${" + output_arg.name + "}", str(output_arg.value))

        # 2.2.2. replace the command variables
        cmd = self.replace_env_variables(cmd)
        cmd = " ".join(cmd.split())

        # 2.3. exec
        # print("cmd:", cmd)
        args = shlex.split(cmd)

        self.service.exec(self.process.metadata, args)

    def replace_env_variables(self, cmd) -> str:
        xml_root_path = os.path.dirname(os.path.abspath(self.process.uri))
        cmd_out = cmd.replace("$__tool_directory__", xml_root_path)
        config = ConfigAccess.instance()
        if config.is_key('env'):
            for element in config.get('env'):
                cmd_out = cmd_out.replace(
                    "${" + element["name"] + "}", element["value"]
                )
        return cmd_out
