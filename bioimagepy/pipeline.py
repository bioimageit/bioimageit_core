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
PipelineRunner
Pipeline
        
"""

import os

from bioimagepy.core.utils import Observable, format_date
from bioimagepy.metadata.run import Run
from bioimagepy.metadata.containers import (RunParameterContainer, RunInputContainer, 
                                            ProcessedDataInputContainer)
from bioimagepy.data import RawData, ProcessedData
from bioimagepy.experiment import Experiment
from bioimagepy.process import Process, ProcessAccess
from bioimagepy.runners.exceptions import RunnerExecError
from bioimagepy.runner import Runner
from bioimagepy.config import ConfigAccess


class PipelineRunner(Observable):
    """Run a process for a pipeline

    Run a process from data in an Experiment and save the
    results in new ProcessedDataset in the experiment

    Parameters
    ----------
    name
        Unique name of the process

    """
    def __init__(self, experiment:Experiment, process:Process):
        Observable.__init__(self)
        self.process = process
        self.experiment = experiment
        # data for runner
        self._output_dataset = ''
        self._process_params = []
        self._inputs_names = []  
        self._inputs_datasets = []   
        self._inputs_query = []  
        self._inputs_origin_output_name = []  
        self._inputs_urls = []

    def set_parameters(self, *args):
        """set the parameters of the process

        Set the parameters to the process using the convention
        'key', 'value' pairs.

        Parameters
        ----------
        args
            Parameters as pairs of arguments

        """
        self._process_params = args 

    def add_input(self, name:str, dataset:str, filter:str='', origin_output_name: str = ''):
        """Add an input data to the process

        Parameters
        ----------
        name
            Name of the input
        dataset
            Name of the dataset containing this input data
        filter
            Regular expression to filter the data to process
        origin_output_name
            name of the origin output if the dataset is a processed
            dataset    

        """
        self._inputs_names.append(name)  
        self._inputs_datasets.append(dataset)  
        self._inputs_query.append(filter) 
        self._inputs_origin_output_name.append(origin_output_name)      

    def add_input_by_urls(self, name: str, urls: list):
        """Add an input (ie data) to the process

        Parameters
        ----------
        name
            Name of the input in the process XML file (ex: -i)

        urls
            Urls of the data to process (urls are the urls of the .md.json file)
       
        """
        self._inputs_names.append(name)
        self._inputs_urls.append(urls)

    def set_dataset_name(self, name:str):
        """Set the name of the dataset where output will be saved

        Parameters
        ----------
        name
            Name of the processed dataset

        """
        self._output_dataset = name

    def man(self):
        """Display the man page of the process."""
        self.process.man()

    def exec(self):
        """Run the process"""
        self.run()

    def run(self):
        """Run the process

        This is the main function that run the process on the experiment data

        Raises
        ------
        RunnerExecError
        
        """
        if self.process.metadata.type == "merge":
            self.run_merged()         
        else:    
            if len(self._inputs_urls) > 0 and len(self._inputs_datasets) > 0:
                raise RunnerExecError("uncompatible inputs. You cannot use both add_input_by_urls and add_input")
            elif len(self._inputs_urls) > 0 and len(self._inputs_datasets) == 0:
                self.run_sequence_by_urls()
            elif len(self._inputs_urls) == 0 and len(self._inputs_datasets) > 0:
                self.run_sequence()
            else:
                raise RunnerExecError("No input. Please use add_input or add_input_by_urls")
        self.experiment.read()    
               

    def run_sequence_by_urls(self):
        """Run the process in a sequence where inputs are data url list

        This is the main function that run the process on the experiment data list

        Raises
        ------
        BiRunnerException
            
        """
        pass

    def run_sequence(self):
        """Run the process in a sequence

        This is the main function that run the process on the experiment data

        Raises
        ------
        RunnerExecError
        
        """
        # 1- Query all the input data and verify that the size 
        # are equal, if not raise an exception
        input_data, data_count = self._query_inputs()            

        # 2- Create the ProcessedDataSet
        processed_dataset = self.experiment.create_processed_dataset(self._output_dataset)

        # 3- Create run
        run = Run()
        run.metadata.process_name = self.process.metadata.fullname()
        run.metadata.process_uri = self.process.uri
        for t in range(len(self._inputs_names)):
            run.metadata.inputs.append(RunInputContainer(
                self._inputs_names[t],
                self._inputs_datasets[t],
                self._inputs_query[t],
                self._inputs_origin_output_name[t]
                )
            )
        for i in range(0, len(self._process_params), 2):
            run.metadata.parameters.append( RunParameterContainer( self._process_params[i], self._process_params[i+1]))

        processed_dataset.add_run(run)

        # 4- loop over the input data
        for i in range(data_count):
  
            data_info_zero = RawData(input_data[0][i].uri())    

            # 4.0- notify observers
            for observer in self._observers:
                notification = dict()
                notification['progress'] = int(100*i/data_count)
                notification['message'] = "Process " + data_info_zero.metadata.name
                observer.notify(notification)

            # 4.1- Parse IO
            args = []
            # get the input arguments
            inputs_metadata = []

            for n in range(len(self._inputs_names)):
                args.append(self._inputs_names[n])
                data_info = RawData(input_data[n][i].uri()) # input data can be a processedData but we only read the common metadata
                args.append(data_info.metadata.uri)

                inp_metadata = ProcessedDataInputContainer()
                inp_metadata.name = self._inputs_names[n]
                inp_metadata.uri = input_data[n][i].uri()
                inp_metadata.type = data_info.metadata.type
                inputs_metadata.append(inp_metadata)

            # get the params arguments
            for param in self._process_params:
                args.append(param)

            # setup outputs
            for output in self.process.metadata.outputs:
                  
                # output metadata
                processedData = ProcessedData()
                processedData.metadata.name = data_info_zero.metadata.name + "_" + output.name
                processedData.metadata.author = ConfigAccess.instance().get('user')['name']
                processedData.metadata.date = format_date('now')
                processedData.metadata.format = output.type

                processedData.metadata.run_uri = run.md_uri
                processedData.metadata.inputs = inputs_metadata

                processedData.metadata.output = {'name': output.name, 'label': output.description}

                processed_dataset.create_data(processedData) # save the metadata and create its md_uri and uri

                # args
                args.append(output.name)
                args.append(processedData.metadata.uri)

            # 4.2- exec    
            runner = Runner(self.process) 
            #print("args = ", args)
            runner.exec(*args)
    
        # 4.0- notify observers
        for observer in self._observers:
            observer.notify({'progress': 100, 'message': 'done'})

    def run_merged(self):
        """Run the process that merge txt number inputs

        This is the main function that run the process on the experiment data

        Raises
        ------
        RunnerExecError
        
        """
        for observer in self._observers:
            observer.notify({'progress': 0, 'message': 'start'}) 

        # 1- Query all the input data and verify that the size 
        # are equal, if not raise an exception
        input_data, data_count = self._query_inputs()            

        # 2- Create the ProcessedDataSet
        processed_dataset = self.experiment.create_processed_dataset(self._output_dataset)

        # 3- Create run
        run = Run()
        run.metadata.process_name = self.process.metadata.fullname()
        run.metadata.process_uri = self.process.uri
        for t in range(len(self._inputs_names)):
            run.metadata.inputs.append(RunInputContainer(
                self._inputs_names[t],
                self._inputs_datasets[t],
                self._inputs_query[t],
                self._inputs_origin_output_name[t]
                )
            )
        for i in range(0, len(self._process_params), 2):
            run.metadata.parameters.append( RunParameterContainer( self._process_params[i], self._process_params[i+1]))

        processed_dataset.add_run(run)

        # 4- merge Inputs
        inputs_values = [0 for i in range(len(self._inputs_names))]
        
        for n in range(len(self._inputs_names)):
            inputs_values[n] = list()
            for i in range(data_count):
                data_info = RawData(input_data[n][i])
                if data_info.metadata.format == "csv" or data_info.metadata.format == "txt":
                    with open(data_info.metadata.uri, 'r') as file:
                        value = file.read().replace('\n', '').replace(' ', '')
                        inputs_values[n].append(value)            
                else:
                    raise RunnerExecError('run merge can use only number datatype')   

        # 5- save data in tmp files files in the processed dataset dir
        tmp_inputs_files = [0 for i in range(len(self._inputs_names))]
        processed_data_dir = processed_dataset.md_uri.replace("processeddataset.md.json", "")
        for n in range(len(self._inputs_names)):
            tmp_inputs_files[n] = os.path.join(processed_data_dir, self._inputs_names[n] + '.csv')
            f = open(tmp_inputs_files[n],'w')
            for i in range(len(inputs_values[n])):
                value = str(inputs_values[n][i])
                if i < len(inputs_values[n])-1:
                    f.write(value + ",")
                else:
                    f.write(value)    
            f.close()         

        # 6- create input metadata for output .md.json
        inputs_metadata = []
        for n in range(len(tmp_inputs_files)):
            inp_metadata = ProcessedDataInputContainer()
            inp_metadata.name = self._inputs_names[n]
            inp_metadata.uri = tmp_inputs_files[n] 
            inp_metadata.type = 'txt'
            inputs_metadata.append(inp_metadata)        

        # 7- run process on generated files
        args = []

        # 7.1- inputs
        for n in range(len(self._inputs_names)):
            args.append(self._inputs_names[n])
            args.append(tmp_inputs_files[n])

        # 7.2- params
        for param in self._process_params:
            args.append(param)

        # 4.3- outputs    
        for output in self.process.metadata.outputs:
            extension = '.' + output.type # type = format for process parameters   
                
            # args
            args.append(output.name)
            output_file_name = output.name
            args.append(os.path.join(processed_data_dir, output_file_name + extension))

            # output metadata
            processedData = ProcessedData()
            processedData.metadata.name = output.name
            processedData.metadata.author = ConfigAccess.instance().get('user')['name']
            processedData.metadata.date = format_date('now')
            processedData.metadata.format = output.type

            processedData.metadata.run_uri = run.md_uri
            processedData.metadata.inputs = inputs_metadata

            processedData.metadata.output = {'name': output.name, 'label': output.description}

            processed_dataset.create_data(processedData) # save the metadata and create its md_uri and uri

        # 8- exec    
        runner = Runner(self.process) 
        runner.exec(*args)   

        # notify observers    
        for observer in self._observers:
            observer.notify({'progress': 100, 'message': 'done'}) 
        
    def _query_inputs(self):
        """Run internal method to exec the query 
        
        Returns
        -------
        input_data: dict
            Dictionnary of the selected inputs data
        data_count: int
            Number of input data

        """

        if len(self._inputs_names) == 0:
            raise RunnerExecError("No input data specified")

        input_data = dict()
        data_count = 0
        for i in range(len(self._inputs_names)):
            input_data[i] = self.experiment.get_data(self._inputs_datasets[i], self._inputs_query[i], self._inputs_origin_output_name[i])
            if i == 0:
                data_count = len(input_data[i]) 
            else:
                if len(input_data[i]) != data_count:
                    raise RunnerExecError("Input dataset queries does not have the same number of data") 
        return [input_data, data_count]         


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
        The list of the processes (PipelineRunner) in the pipeline

    """
    def __init__(self, experiment:Experiment=None):
        self.experiment = experiment
        self.processes = list()

    def add_process(self, process=Process):
        """Add a process to the pipeline
        
        Parameters
        ----------
        process
            instance of Process class

        Returns
        -------
        the PipelineRunner associated to the process

        """
        pipelineRunner = PipelineRunner(self.experiment, process)
        self.processes.append(pipelineRunner)
        return pipelineRunner

    def add_process_by_name(self, name:str):
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
        process = ProcessAccess().get(name)
        return self.add_process(process)

    def add_process_by_uri(self, uri:str):
        """Add a process to the pipeline
        
        The process is created using it URI (xml file)
        
        Parameters
        ----------
        uri
            URI of the process XML file

        Returns
        -------
        Process
            The object containing the process.

        """
        return self.add_process(Process(uri))        

    def run(self):
        """Run the pipeline"""
        for process in self.processes:
            process.run()

