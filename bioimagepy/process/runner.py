from ..metadata import experiment
from ..metadata import metadata
from ..metadata.dataset import BiDataSet, BiProcessedData, BiRawDataSet
import os

class BiRunnerException(Exception):
   """Raised when an error occure in the run of a process"""
   pass

class BiProcessRunner(): 
    """Abstract class that store a data metadata"""
    def __init__(self, experiment : experiment.BiExperiment):
        self._objectname = "BiData"  
        self._experiment = experiment
        self._inputs_names = []
        self._inputs_datasets = []
        self._inputs_query = []
        self._output_names = []

    def set_process(self, function_name :str, **params):
        self._function_name = function_name
        self._function_param = params 

    def add_input(self, name: str, dataset: str, query: str):
        self._inputs_names.append(name)  
        self._inputs_datasets.append(dataset)  
        self._inputs_query.append(query)   

    def add_output(self, name: str):
        self._output_names.append(name)     

    def run(self):
        # 1- query all the input data and verify that the size 
        # are equal, if not raise an exception
        if len(self._inputs_names) == 0:
            raise BiRunnerException("No input data specified")

        input_data = dict()
        data_count = 0
        for i in range(len(self._inputs_names)):
            input_data[i] = experiment.query(self._experiment, self._inputs_datasets[i], self._inputs_query[i])
            if i == 0:
                data_count = len(input_data[i]) 
            else:
                if len(input_data[i]) != data_count:
                    raise BiRunnerException("Input dataset queries does not have the same number of data")            

        # 2- create the ProcessedDataSet and register it to the Experiment
        # 2.1 create the ProcessedDataSet
        process_name = self._function_name.replace(' ', '_')
        processed_data_dir = os.path.join(self._experiment.dir(), process_name)
        incr = 0
        while os.path.isdir( processed_data_dir ):
            incr += 1 
            processed_data_dir += "_" + incr
            process_name +=  "_" + incr

        if not os.mkdir(processed_data_dir):
            raise BiRunnerException("Unable to create the process directory: " + processed_data_dir)

        processed_dataset_md_file = os.path.join(processed_data_dir, "processeddataset.md.json")
        open(processed_dataset_md_file, 'a').close()
        processed_dataset = BiProcessedData(processed_dataset_md_file)
        processed_dataset.name = process_name
        processed_dataset.write()

        # 2.2- Register the ProcessedDataSet to the Experiment  
        self._experiment.metadata['processeddatasets'].append(process_name) 
        self._experiment.write()

        # 3- loop over the input data
        for i in range(input_data):
            print('Process data: ')
            # TODO: implement this loop
        #     3.1- run the process
        #     3.2- create a md.json file for each output (known from the xml file or add output)
        #     3.3- register the md.json file to the ProcessedDataSet  
          