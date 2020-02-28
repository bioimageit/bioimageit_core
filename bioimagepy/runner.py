# -*- coding: utf-8 -*-
"""runner module.

This module contains the BiRunnerExperiment class that allows to run processes
on an BiExperiment data (raw data and processed data). Results are automatically
stored and indexed in a new BiProcessedDataSet in the BiExperiment

Example
-------
    Here is an example of how to run a process on all the data of the RawDataSet called 'data'
    and where the tag 'Population'='population1':

        >>> from bioimagepy.runner import BiRunnerExperiment
        >>> runner = BiRunnerExperiment(myexperiment)   
        >>> runner.set_process('/path/to/process/svdeconv2d.xml',
        >>>                '-sigma', '3', '-weighting', '0.1', '-regularization', '2') 
        >>> runner.add_input('-i', 'data', 'Population=population1 AND ID=002')
        >>> runner.run()

Classes
-------
BiRunnerExperiment

Raises
------
BiRunnerException

"""

from .metadata import BiData, BiDataSet, BiProcessedData, BiRawDataSet, BiProcessedDataSet, BiRun
from .process import BiProcess, DATA_IMAGE, DATA_TXT, DATA_NUMBER, DATA_ARRAY, DATA_MATRIX, DATA_TABLE
from .core import BiProgressObserver, BiConfig
import bioimagepy.experiment as experiment
import os
import datetime
import ntpath

class BiRunnerException(Exception):
   """Raised when an error occure in the run of a process"""
   pass

class BiRunnerExperiment(): 
    """Class to run a process on a BiExperiment data

    The process runner needs an experiment, a process XML description file, 
    a query on the experiment data to select the process inputs and the process
    parameters. The experiment is given in the constructor whereas the other
    arguments are given using setters (see example in the module doc)

    Parameters
    ----------
        md_file_url (str): Path of the experiment.md.json file.

    Attributes
    ----------
        metadata (tuple): json metadata description.

    """ 
    def __init__(self, experiment : experiment.BiExperiment):
        self._objectname = "BiData"  
        self._observers = []
        self._experiment = experiment
        self._inputs_names = []
        self._inputs_datasets = []
        self._inputs_query = []
        self._inputs_urls = []
        self._output_names = []
        self._process = None
        self._process_params = [] 
        self.author = 'unknown'
        self._inputs_origin_output_name = []
        self._output_dataset = ""
        self.config = None

    def set_config(self, config: BiConfig):
        self.config = config    

    def add_observer(self, observer: BiProgressObserver):
        self._observers.append(observer)    

    def set_author(self, author: str):
        self.author = author

    def set_process(self, process_xml_file :str, *params):
        """set the runner process

        Parameters
        ----------
        process_xml_file
            URL of the XML file describing the process

        *params
            List of the parameters (ex: "-sigma, 2, -weighting, 7")    

        """

        self._process = BiProcess(process_xml_file)
        if self.config:
            self._process.setConfig(self.config)
        self._process_params = params 


    def add_input(self, name: str, dataset: str, query: str, origin_output_name: str = ''):
        """Add an input (ie data) to the process

        Parameters
        ----------
        name
            Name of the input in the process XML file (ex: -i)

        dataset
            Name of the dataset where the data come from (ex: data)

        query
            Query to filter the data (ex: "Population=population1") leave blank for no filtering        

        """

        self._inputs_names.append(name)  
        self._inputs_datasets.append(dataset)  
        self._inputs_query.append(query) 
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
    

    def setOutputDataSet(self, name :str):
        self._output_dataset = name

    def exec(self):
        """Run the process

        This is a convenient function for API

        """

        self.run()


    def run(self):
        """Run the process

        This is the main function that run the process on the experiment data

        Raises
        ------
        BiRunnerException
        
        """

        if self._process.info.type == "sequential":
            if len(self._inputs_urls) > 0 and len(self._inputs_datasets) > 0:
                raise BiRunnerException("uncompatible inputs. You cannot use both add_input_by_urls and add_input")
            elif len(self._inputs_urls) > 0 and len(self._inputs_datasets) == 0:
                self.run_sequence_by_urls()
            elif len(self._inputs_urls) == 0 and len(self._inputs_datasets) > 0:
                self.run_sequence()
            else:
                raise BiRunnerException("No input. Please use add_input or add_input_by_urls")
        else:
            self.run_merged()    

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
            raise BiRunnerException("No input data specified")

        input_data = dict()
        data_count = 0
        for i in range(len(self._inputs_names)):
            input_data[i] = experiment.query(self._experiment, self._inputs_datasets[i], self._inputs_query[i], self._inputs_origin_output_name[i])
            if i == 0:
                data_count = len(input_data[i]) 
            else:
                if len(input_data[i]) != data_count:
                    raise BiRunnerException("Input dataset queries does not have the same number of data") 
        return [input_data, data_count]            

    def _create_processeddataset(self):
        """Run internal method to create the processed dataset 
        
        Returns
        -------
        processed_dataset
            Instance of the created dataset
            
        processed_data_dir
            URL of the directory containing the processeddataset

        """

        # Create the ProcessedDataSet
        process_name = self._process.info.name.replace(' ', '_')
        processed_data_dir = os.path.join(self._experiment.dir(), process_name)
        incr = 0
        process_name_no_incr = process_name
        processed_data_dir_no_incr = processed_data_dir
        while os.path.isdir( processed_data_dir ):
            incr += 1 
            processed_data_dir = processed_data_dir_no_incr + "_" + str(incr)
            process_name = process_name_no_incr +  "_" + str(incr)

        #print('processed_data_dir:', processed_data_dir)
        try:
            os.makedirs(processed_data_dir)
        except OSError as e:
            raise BiRunnerException("Unable to create the process directory: " + processed_data_dir + ', err:', e)

        processed_dataset_md_file = os.path.join(processed_data_dir, "processeddataset.md.json")
        open(processed_dataset_md_file, 'a').close()
        processed_dataset = BiProcessedDataSet(processed_dataset_md_file)
        processed_dataset.metadata['name'] = process_name
        processed_dataset.write()

        # Register the ProcessedDataSet to the Experiment  
        self._experiment.metadata['processeddatasets'].append( os.path.join(process_name, "processeddataset.md.json") ) 
        self._experiment.write()

        return [processed_dataset, processed_data_dir]

    def _create_runfile(self, processed_data_dir: str) -> str:
        """Run internal method to write the run metadata file

        Parameters
        ----------
        processed_data_dir
            Destination directory for the processed dataset

        """

        run_md_file_name = "run.md.json"
        runid_count = 0
        while ( os.path.isfile(os.path.join(processed_data_dir, run_md_file_name)) ):
            existingRun = BiRun(os.path.join(processed_data_dir, run_md_file_name))
            if existingRun.process_name() != self._process.info.name:
                raise BiRunnerException("You can only run " + self._process.info.name + " in the dataset " + self._output_dataset)
            runid_count += 1
            run_md_file_name = "run_"+str(runid_count)+".md.json"

        run_md_file = os.path.join(processed_data_dir, run_md_file_name)
        open(run_md_file, 'a').close()
        run_metadata = BiRun(run_md_file) 
        run_metadata.set_process_name(self._process.info.name)
        run_metadata.set_process_url(self._process.info.xml_file_url)
        for i in range(0, len(self._process_params), 2):
            run_metadata.add_arameter(self._process_params[i], self._process_params[i+1])
        run_metadata.set_processeddataset("processeddataset.md.json")

        
        if len(self._inputs_urls) > 0:
            for t in range(len(self._inputs_names)):
                urls = []
                for url in self._inputs_urls[t]:
                    urll = url.replace(self._experiment.md_file_dir() , "..")
                    urls.append(urll)

                run_metadata.add_input_list(        
                                    self._inputs_names[t],  
                                    urls
                )  
        else:
            for t in range(len(self._inputs_names)):
                run_metadata.add_input(
                    self._inputs_names[t],
                    self._inputs_datasets[t],
                    self._inputs_query[t],
                    self._inputs_origin_output_name[t]
                )

        run_metadata.write()
        return run_md_file_name

    def run_sequence(self):
        """Run the process in a sequence

        This is the main function that run the process on the experiment data

        Raises
        ------
        BiRunnerException
        
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


    def run_sequence_by_urls(self):
        """Run the process in a sequence where inputs are data url list

        This is the main function that run the process on the experiment data list

        Raises
        ------
        BiRunnerException
            
        """
 
        # 1- Query all the input data and verify that the size 
        # are equal, if not raise an exception
        input_data = self._inputs_urls
        data_count = len(self._inputs_urls[0])          

        # 2- Create the ProcessedDataSet and register it to the Experiment
        if not self._output_dataset:
            processed_dataset, processed_data_dir = self._create_processeddataset()
        else:
            processed_dataset = self._experiment.processeddataset_by_name(self._output_dataset)
            processed_data_dir = processed_dataset.md_file_dir()

        # 3- create the run.md.json file
        run_md_file_name = self._create_runfile(processed_data_dir)

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
                if output.type == DATA_IMAGE():
                    extension = '.tif'
                elif output.type == DATA_TXT(): 
                    extension = '.txt' 
                elif output.type == DATA_NUMBER() or output.type == DATA_ARRAY() or output.type == DATA_MATRIX() or output.type == DATA_TABLE(): 
                    extension = '.csv'     
                    
                input_basename = ntpath.basename(input_data[0][i])
                output_file_name = input_basename.replace('.md.json', '') + "_" + output.name

                idx = 0
                while os.path.exists( os.path.join(processed_data_dir, output_file_name + ".md.json") ):
                    idx += 1
                    output_file_name = input_basename.replace('.md.json', '') + "_" + output.name + "_" + str(idx)

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
                output_data.metadata["origin"]['runurl'] = run_md_file_name
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


    def _now_date(self) -> str:
        """Get the date

        Returns
        -------
            The current date in the format yyyy-mm-dd

        """

        now = datetime.datetime.now()
        monthStr = str(now.month)
        if now.month < 10:
            monthStr = '0' + monthStr
        dayStr = str(now.day)
        if now.day < 10:   
            dayStr = '0' + dayStr 

        return str(now.year) + '-' + monthStr + '-' + dayStr  

    def _get_output_extension(self, datatype: str) -> str:
        """Select a file extension depending on the datatype

        Parameters
        ----------
        datatype
            Type of data available in at metadata.DATA_XXX()

        Returns
        -------
            The selected file extension
        """

        extension = '.dat'
        if datatype == DATA_IMAGE():
            extension = '.tif'
        elif datatype == DATA_TXT(): 
            extension = '.txt' 
        elif datatype == DATA_NUMBER() or datatype == DATA_ARRAY() or datatype == DATA_MATRIX() or datatype == DATA_TABLE(): 
            extension = '.csv' 
        return extension            

    def run_merged(self):
        """Run the process merging the inputs

        This is the main function that run the process on the experiment data

        Raises
        ------
        BiRunnerException
        
        """

        # 1- Query all the input data and verify that the size 
        # are equal, if not raise an exception
        input_data, data_count = self._query_inputs()            

        # 2- Create the ProcessedDataSet and register it to the Experiment
        processed_dataset, processed_data_dir = self._create_processeddataset()

        # 3- create the run.md.json file
        self._create_runfile(processed_data_dir)

        # 4- merge Inputs
        inputs_values = [0 for i in range(len(self._inputs_names))]
        
        for n in range(len(self._inputs_names)):
            inputs_values[n] = list()
            for i in range(data_count):
                data_info = BiData(input_data[n][i])
                if data_info.datatype() == DATA_NUMBER() or data_info.datatype() == "csv" or data_info.datatype() == "txt":
                    with open(data_info.url(), 'r') as file:
                        value = file.read().replace('\n', '').replace(' ', '')
                        inputs_values[n].append(value)            
                else:
                    raise BiRunnerException('run merge can use only number datatype')    
        
        # 3- save data in tmp files or hidden files in the output dir
        tmp_inputs_files = [0 for i in range(len(self._inputs_names))]
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

        # create input metadata for output .md.json
        inputs_metadata = []
        for n in range(len(tmp_inputs_files)):
            inp_metadata = dict()
            inp_metadata["name"] = self._inputs_names[n]
            inp_metadata["url"] = tmp_inputs_files[n] 
            inputs_metadata.append(inp_metadata)        

        # 4- run process on generated files
        args = []

        # 4.1- inputs
        for n in range(len(self._inputs_names)):
            args.append(self._inputs_names[n])
            args.append(tmp_inputs_files[n])

        # 4.2- params
        for param in self._process_params:
            args.append(param)

        # 4.3- outputs    
        for output in self._process.info.outputs:
            extension = self._get_output_extension(output.type)   
                
            # args
            args.append(output.name)
            output_file_name = output.name
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
        
        # 4.4- exec    
        print("args:", args)
        self._process.exec(*args)
