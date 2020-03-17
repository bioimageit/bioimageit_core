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

class ProcessNotFoundError(Exception):
   """Raised when a process is not found"""
   pass


class Process():
    def __init__(self, name:str):
        self.name=name
        self.info=None # Process Info


    def man(self):
        """Display the process man page of the process. The man information are 
        collected from the XML file 
        
        """

        # 1. program name
        print(self.info.name, ':', self.info.description)
        # 2. list of args key, default, description
        for param in self.info.inputs:
            line_new = '\t{:>15}\t{:>15}\t{:>15}'.format(param.name, param.default_value, param.description)
            print(line_new)
        for param in self.info.outputs:
            line_new = '\t{:>15}\t{:>15}\t{:>15}'.format(param.name, param.default_value, param.description)
            print(line_new) 

    def run(self, *parameters):
        pass

    def exec(self, *parameters):
        pass
