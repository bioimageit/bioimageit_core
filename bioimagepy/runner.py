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

from bioimagepy.runners.factory import runnerServices
from bioimagepy.process import Process

class Runner():
    def __init__(self, process:Process):
        self.process=process
        self.service = runnerServices.get('LOCAL')

    def man(self):
        """Convenient method to print the process man"""
        self.process.man()

    def run(self, *parameters):
        pass

    def exec(self, *parameters):
        pass
