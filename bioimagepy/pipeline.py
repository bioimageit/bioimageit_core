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

from bioimagepy.core.utils import Observable
from bioimagepy.experiment import Experiment
from bioimagepy.process import Process, ProcessAccess
from bioimagepy.runners.exceptions import RunnerExecError


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
        self._process_params = None
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

    def add_input(self, name:str, dataset:str, filter:str, origin_output_name: str = ''):
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
        if self.process.metadata.type == "sequential":
            if len(self._inputs_urls) > 0 and len(self._inputs_datasets) > 0:
                raise RunnerExecError("uncompatible inputs. You cannot use both add_input_by_urls and add_input")
            elif len(self._inputs_urls) > 0 and len(self._inputs_datasets) == 0:
                self.run_sequence_by_urls()
            elif len(self._inputs_urls) == 0 and len(self._inputs_datasets) > 0:
                self.run_sequence()
            else:
                raise RunnerExecError("No input. Please use add_input or add_input_by_urls")
        else:
            self.run_merged()    

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

        # 2- Create the ProcessedDataSet and register it to the Experiment
        processed_dataset, processed_data_dir = self._create_processeddataset()

        # 3- create the run.md.json file
        self._create_runfile(processed_data_dir)

        # 4- loop over the input data
        for i in range(data_count):

            # 4.0- notify observers
            for observer in self._observers:
                notification = dict()
                notification['progress'] = int(100*i/data_count)
                notification['message'] = "Process " + ntpath.basename(input_data[0][i])
                observer.notify(notification)

            # 4.1- Parse IO
            args = []
            # get the input arguments
            inputs_metadata = []
            for n in range(len(self._inputs_names)):
                args.append(self._inputs_names[n])
                data_info = BiData(input_data[n][i])
                args.append(data_info.url())

                inp_metadata = dict()
                inp_metadata["name"] = self._inputs_names[n]

                inp_metadata["url"] = '..' + input_data[n][i].replace(self._experiment.md_file_dir(), '') 
                inputs_metadata.append(inp_metadata)

            # get the params arguments
            for param in self._process_params:
                args.append(param)

            # setup outputs
            for output in self._process.info.outputs:
                extension = '.dat'
                if output.type == DATA_IMAGE() or output.type == "tiff" or output.type == "tif":
                    extension = '.tif'
                elif output.type == DATA_TXT(): 
                    extension = '.txt' 
                elif output.type == DATA_NUMBER() or output.type == DATA_ARRAY() or output.type == DATA_MATRIX() or output.type == DATA_TABLE() or output.type == "csv": 
                    extension = '.csv'     
                
                input_basename = ntpath.basename(input_data[0][i])
                output_file_name = input_basename.replace('.md.json', '') + "_" + output.name

                # args
                args.append(output.name)
                args.append(os.path.join(processed_data_dir, output_file_name + extension))

                # md.json file
                output_data_md_file = os.path.join(processed_data_dir, output_file_name + ".md.json")
                open(output_data_md_file, 'a').close()
                output_data = BiProcessedData(output_data_md_file)
                output_data.metadata["common"] = dict()
                output_data.metadata["common"]['name'] = output_file_name
                output_data.metadata["common"]['url'] = output_file_name + extension


                output_data.metadata["common"]['createddate'] = self._now_date()
                output_data.metadata["common"]['author'] = self.author
                output_data.metadata["common"]['datatype'] = output.type
                output_data.metadata["origin"] = dict()
                output_data.metadata["origin"]['type'] = 'processed'
                output_data.metadata["origin"]['runurl'] = 'run.md.json'
                output_data.metadata["origin"]['inputs'] = inputs_metadata
                output_data.metadata["origin"]["output"] = dict()
                output_data.metadata["origin"]["output"]["name"] = output.name
                output_data.metadata["origin"]["output"]["label"] = output.description
                output_data.write()
                processed_dataset.metadata['urls'].append(output_file_name + ".md.json")
                processed_dataset.write()

            # 4.2- exec    
            #print("args:", args)
            self._process.exec(*args)

    def run_merged(self):
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

