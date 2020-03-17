# -*- coding: utf-8 -*-
"""pipeline module.

This module contains the Pipeline class that allows to design a pipeline
to process data contained in an Experiment 

Example
-------
    Here is an example of how to write a Pipeline:

        >>> from bioimagepy.experiment import Experiment
        >>> from bioimagepy.pipeline import Pipeline
        >>> 
        >>> mypipeline = Pipeline(Experiment('my/experiment/uri'))
        >>>
        >>> p1 = mypipeline.add_process('svdeconv2d')
        >>> p1.set_parameters('sigma', '3', 'weighting', '0.1', 'regularization', '2')
        >>> p1.add_input('i', 'data', '')
        >>> p1.set_dataset_name('deconv2d')
        >>>
        >>> p2 = mypipeline.add_process('particleanalyzer')
        >>> p2.set_parameters('threshold', 'Default dark')
        >>> p2.add_input('i', 'deconv', '')
        >>> p2.set_dataset_name('particles')
        >>>
        >>> mypipeline.run()

Classes
-------
PipelineProcess
Pipeline
        
"""

from bioimagepy.experiment import Experiment
#from bioimagepy.process import ProcessNotFoundError


class PipelineProcess():
    """Run a process for a pipeline

    Run a process from data in an Experiment and save the
    results in new ProcessedDataset in the experiment

    Parameters
    ----------
    name
        Unique name of the process

    """
    def __init__(self, name:str):
        self._process = Process(name)
        self._processed_dataset_name = ''
        pass

    def set_parameters(self, *args):
        """set the parameters of the process

        Set the parameters to the process using the convention
        'key', 'value' pairs.

        Parameters
        ----------
        args
            Parameters as pairs of arguments

        """
        self.process.set_parameters(args)

    def add_input(self, name:str, dataset:str, filter:str):
        """Add an input data to the process

        Parameters
        ----------
        name
            Name of the input
        dataset
            Name of the dataset containing this input data
        filter
            Regular expression to filter the data to process

        """
        # TODO add here the code to the actual ExperimentRunner
        pass     

    def set_dataset_name(self, name:str):
        """Set the name of the dataset where output will be saved

        Parameters
        ----------
        name
            Name of the processed dataset

        """
        self._processed_dataset_name = name

    def man(self):
        """Display the man page of the process."""
        self.process.man()

    def run(self):
        """Run the process"""
        # TODO get the implementation from ExperimentRunner
        pass    


class Pipeline():
        """Class that store a raw data metadata
    
    RawData allows to read/write and manipulate the metadata
    of a raw data.

    Parameters
    ----------
    experiment
        the Experiment where the process runs

    Attributes
    ----------
    experiment
        The Experiment where the process runs
    processes
        The list of the processes (PipelineProcess) in the pipeline

    """
    def __init__(self, experiment:Experiment=None):
        self.experiment = experiment
        self.processes = list()

    def add_process(self, name=''):
        """Add a process to the pipeline
        
        The process is created by searching the process
        in the database.
        
        Parameters
        ----------
        name
            Name of the process to create

        Returns
        -------
        Process
            The object containing the process.

        Raises
        ------
        ProcessNotFoundError
            If the process is not found in the database.

        """
        pass

    def run(self):
        """Run the pipeline"""
        for process in self.processes:
            process.run()

