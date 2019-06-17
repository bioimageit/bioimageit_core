from .metadata import BiData, BiDataSet, BiProcessedData, BiRawDataSet, BiProcessedDataSet, BiRun
from .process import BiProcess, DATA_IMAGE, DATA_TXT
import bioimagepy.experiment as experiment
import os
import datetime
import ntpath

class BiRunnerException(Exception):
   """Raised when an error occure in the run of a process"""
   pass

class BiRunnerExperiment(): 
    """Class to run a process on en Experiment"""
    def __init__(self, experiment : experiment.BiExperiment):
        self._objectname = "BiData"  
        self._experiment = experiment
        self._inputs_names = []
        self._inputs_datasets = []
        self._inputs_query = []
        self._output_names = []
        self._process = None
        self._process_params = [] 

    def set_process(self, process_xml_file :str, *params):
        self._process = BiProcess(process_xml_file)
        self._process_params = params 

    def add_input(self, name: str, dataset: str, query: str):
        self._inputs_names.append(name)  
        self._inputs_datasets.append(dataset)  
        self._inputs_query.append(query)       

    def exec(self):
        self.run()

    def run(self):
        # 1- Query all the input data and verify that the size 
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

        # 2- Create the ProcessedDataSet and register it to the Experiment
        # 2.1 Create the ProcessedDataSet
        process_name = self._process.info.name.replace(' ', '_')
        processed_data_dir = os.path.join(self._experiment.dir(), process_name)
        incr = 0
        process_name_no_incr = process_name
        processed_data_dir_no_incr = processed_data_dir
        while os.path.isdir( processed_data_dir ):
            incr += 1 
            processed_data_dir = processed_data_dir_no_incr + "_" + str(incr)
            process_name = process_name_no_incr +  "_" + str(incr)

        print('processed_data_dir:', processed_data_dir)
        try:
            os.makedirs(processed_data_dir)
        except OSError as e:
            raise BiRunnerException("Unable to create the process directory: " + processed_data_dir + ', err:', e)

        processed_dataset_md_file = os.path.join(processed_data_dir, "processeddataset.md.json")
        open(processed_dataset_md_file, 'a').close()
        processed_dataset = BiProcessedDataSet(processed_dataset_md_file)
        processed_dataset.metadata['name'] = process_name
        processed_dataset.write()

        # 2.2- Register the ProcessedDataSet to the Experiment  
        self._experiment.metadata['processeddatasets'].append( os.path.join(process_name, "processeddataset.md.json") ) 
        self._experiment.write()

        # 3- create the run.md.json file
        run_md_file = os.path.join(processed_data_dir, "run.md.json")
        open(run_md_file, 'a').close()
        run_metadata = BiRun(run_md_file)
        run_metadata.set_process_name(self._process.info.name)
        run_metadata.set_process_url(self._process.info.xml_file_url)
        for i in range(0, len(self._process_params), 2):
            run_metadata.add_arameter(self._process_params[i], self._process_params[i+1])
        run_metadata.set_processeddataset("processeddataset.md.json")
        run_metadata.write()

        # 4- loop over the input data
        for i in range(data_count):
            print('Process data: ', i, '/', len(input_data))
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
                now = datetime.datetime.now()
                monthStr = str(now.month)
                if now.month < 10:
                    monthStr = '0' + monthStr
                dayStr = str(now.day)
                if now.day < 10:   
                    dayStr = '0' + dayStr 

                output_data.metadata["common"]['createddate'] = str(now.year) + '-' + monthStr + '-' + dayStr
                output_data.metadata["common"]['author'] = 'Unknown' # TODO git this value on the app settings
                output_data.metadata["common"]['datatype'] = output.type
                output_data.metadata["origin"] = dict()
                output_data.metadata["origin"]['type'] = 'processed'
                output_data.metadata["origin"]['runurl'] = 'run.md.json'
                output_data.metadata["origin"]['inputs'] = inputs_metadata
                output_data.write()
                print('processeddataset metadata: ', processed_dataset.metadata)
                print('processed_dataset file', processed_dataset._md_file_url)
                processed_dataset.metadata['urls'].append(output_file_name + ".md.json")
                processed_dataset.write()


            # 4.2- exec    
            print("args:", args)
            self._process.exec(*args)

          