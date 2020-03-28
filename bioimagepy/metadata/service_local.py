# -*- coding: utf-8 -*-
"""BioImagePy local metadata service.

This module implements the local service for metadata
(Data, DataSet and Experiment) management.
This local service read/write and query metadata from a database
made od JSON file in the file system  

Classes
------- 
MetadataServiceProvider

"""

import os
import os.path
import json
from shutil import copyfile

from bioimagepy.metadata.exceptions import MetadataServiceError
from bioimagepy.metadata.containers import (METADATA_TYPE_RAW, METADATA_TYPE_PROCESSED, 
                                            RawDataContainer, ProcessedDataContainer,
                                            ProcessedDataInputContainer, DataSetContainer,
                                            ExperimentContainer, RunContainer, RunInputContainer,
                                            RunParameterContainer)


def md_file_path(md_uri:str) -> str:
    """get metadata file directory path

    Returns
    ----------
    str
        The name of the metadata file directory path

    """
    abspath = os.path.abspath(md_uri)
    return os.path.dirname(abspath)

def relative_path(file:str, reference_file:str):
    """convert file absolute path to a relative path wrt reference_file

    Parameters
    ----------
    reference_file
        Reference file 
    file
        File to get absolute path   

    Returns
    -------
    relative path of uri wrt md_uri  

    """
    separator = os.sep
    file = file.replace(separator+separator, separator)
    reference_file = reference_file.replace(separator+separator, separator)

    for i in range(len(file)):
        common_part = reference_file[0:i]
        if not common_part in file:
            break

    last_separator = common_part.rfind(separator)

    shortreference_file = reference_file[last_separator+1:]

    numberOfSubFolder = shortreference_file.count(separator)
    shortfile = file[last_separator+1:]
    for i in range(numberOfSubFolder):
        shortfile = '..' + separator + shortfile

    return shortfile

def absolute_path(file:str, reference_file:str):
    """convert file relative ro referenceFilte into an absolut path

    Parameters
    ----------
    reference_file
        Reference file 
    file
        File to get absolute path   

    Returns
    -------
    relative path of uri wrt md_uri  

    """
    if os.path.isfile(file):
        return os.path.abspath(file)

    separator = os.sep
    last_separator = reference_file.rfind(separator)    
    canonical_path = reference_file[0:last_separator+1]
    return simplify_path(canonical_path + file)

def simplify_path(path:str) -> str:
    """Simplify a path by removing ../"""

    if path.find('..') < 0:
        return path

    separator = os.sep
    keep_folders = path.split(separator)

    found = True
    while found:
        pos = -1
        folders = keep_folders
        for i in range(len(folders)):
            if folders[i] == '..':
                pos = i
                break    
        if pos > -1:  
            keep_folders = []  
            for i in range(0,pos-1):  
                keep_folders.append(folders[i])
            for i in range(pos+1,len(folders)):
                keep_folders.append(folders[i])
        else:
            found = False        

    clean_path = ''
    for i in range(len(keep_folders)):
        clean_path += keep_folders[i] 
        if i < len(keep_folders)-1:
            clean_path += separator     
    return clean_path


class LocalMetadataServiceBuilder:
    """Service builder for the metadata service"""
    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = LocalMetadataService()
        return self._instance

class LocalMetadataService:
    """Service for local metadata management

    """
    def __init__(self):
        self.service_name = 'LocalMetadataService'

    def _read_json(self, md_uri: str):
        """Read the metadata from the a json file"""
        if os.path.getsize(md_uri) > 0:
            with open(md_uri) as json_file:  
                return json.load(json_file)

    def _write_json(self, metadata: dict, md_uri: str):
        """Write the metadata to the a json file"""
        with open(md_uri, 'w') as outfile:
            json.dump(metadata, outfile, indent=4)     

    def read_rawdata(self, md_uri: str) -> RawDataContainer:
        if os.path.isfile(md_uri): 
            metadata = self._read_json(md_uri)
            container = RawDataContainer()
            container.type = metadata['origin']['type']
            container.name = metadata['common']['name']
            container.author = metadata['common']['author']
            container.date = metadata['common']['date']
            container.format = metadata['common']['format']
            # copy the url if absolute, append md_uri path otherwise
            container.uri = absolute_path(metadata['common']['url'], md_uri)  
            for key in metadata['tags']:
                container.tags[key] = metadata['tags'][key]    
            return container
        return RawDataContainer()    

    def write_rawdata(self, container: RawDataContainer, md_uri: str):
        metadata = dict()
        
        metadata['origin'] = dict()
        metadata['origin']['type'] = METADATA_TYPE_RAW()
        
        metadata['common'] = dict()
        metadata['common']['name'] = container.name
        metadata['common']['author'] = container.author
        metadata['common']['date'] = container.date
        metadata['common']['format'] = container.format
        metadata['common']['url'] = relative_path(container.uri, md_uri)

        metadata['tags'] = dict()
        for key in container.tags:
            metadata['tags'][key] = container.tags[key]

        self._write_json(metadata, md_uri)

    def read_processeddata(self, md_uri: str) -> ProcessedDataContainer:
        if os.path.isfile(md_uri): 
            metadata = self._read_json(md_uri)
            container = ProcessedDataContainer()
            container.name = metadata['common']['name']
            container.author = metadata['common']['author']
            container.date = metadata['common']['date']
            container.format = metadata['common']['format']
            container.uri = absolute_path(metadata['common']['url'], md_uri)
            # origin run
            container.run_uri = absolute_path(metadata['origin']['runurl'], md_uri)
            # origin input
            for input in metadata['origin']['inputs']:
                container.inputs.append(ProcessedDataInputContainer(input['name'], absolute_path(input['url'], md_uri), input['type']))
            # origin 
            if 'name' in metadata['origin']['output']:     
                container.output['name'] = metadata['origin']['output']["name"]
            if 'label' in metadata['origin']['output']:    
                container.output['label'] = metadata['origin']['output']['label']
                   
            return container
        return ProcessedDataContainer() 

    def write_processeddata(self, container: ProcessedDataContainer, md_uri: str):
        metadata = dict()
        # common
        metadata['common'] = dict()
        metadata['common']['name'] = container.name
        metadata['common']['author'] = container.author
        metadata['common']['date'] = container.date
        metadata['common']['format'] = container.format
        metadata['common']['url'] = relative_path(container.uri, md_uri)
        # origin type
        metadata['origin'] = dict()
        metadata['origin']['type'] = METADATA_TYPE_PROCESSED()
        # run url
        metadata['origin']['runurl'] = relative_path(container.run_uri, md_uri)
        # origin inputs
        metadata['origin']['inputs'] = list()
        for input in container.inputs:
            metadata['origin']['inputs'].append({'name':input.name,'url':relative_path(input.uri,md_uri), 'type':input.type})
        # origin ouput
        metadata['origin']['output'] = {'name':container.output['name'],'label':container.output['label']}
               
        self._write_json(metadata, md_uri)

    def read_rawdataset(self, md_uri: str) -> DataSetContainer: 
        if os.path.isfile(md_uri): 
            metadata = self._read_json(md_uri)
            container = DataSetContainer()
            container.name = metadata['name']
            for uri in metadata['urls']:
                container.uris.append(absolute_path(uri, md_uri))

            return container
        return DataSetContainer()  

    def write_rawdataset(self, container: DataSetContainer, md_uri: str):  
        metadata = dict()
        metadata['name'] = container.name
        metadata['urls'] = list()
        for uri in container.uris:
            metadata['urls'].append( relative_path(uri, md_uri ) )
        self._write_json(metadata, md_uri)      
    
    def read_processeddataset(self, md_uri: str) -> DataSetContainer: 
        if os.path.isfile(md_uri): 
            metadata = self._read_json(md_uri)
            container = DataSetContainer()
            container.name = metadata['name']
            for uri in metadata['urls']:
                container.uris.append(absolute_path(uri, md_uri))

            return container
        return DataSetContainer()        

    def write_processeddataset(self, container: DataSetContainer, md_uri: str):  
        metadata = {}
        metadata['name'] = container.name
        metadata['urls'] = list()
        for uri in container.uris:
            metadata['urls'].append( relative_path(uri, md_uri ) )
        self._write_json(metadata, md_uri)     

    def add_run_processeddataset(self, run:RunContainer, dataset_md_uri:str):
        """Add a run to a processed dataset

        Parameters
        ----------
        run
            Container of the Run metadata
        dataset_md_uri
            URI of the ProcessedDataset     

        """
        # create run URI
        dataset_dir = md_file_path(dataset_md_uri)
        run_md_file_name = "run.md.json"
        runid_count = 0
        while ( os.path.isfile(os.path.join(dataset_dir, run_md_file_name)) ):
            runid_count += 1
            run_md_file_name = "run_"+str(runid_count)+".md.json"
        run_uri = os.path.join(dataset_dir, run_md_file_name)   

        # write run
        self.write_run(run, run_uri)


    def create_processed_dataset(self, name:str, experiment_md_uri: str):
        """create a new processed dataset

        Parameters
        ----------
        name
            Name of the processed dataset
        experiment_md_uri
            URI of the experiment that contains the dataset    

        """
        experiment_dir = md_file_path(experiment_md_uri)
        processeddataset_uri = os.path.join(experiment_dir, name, '.md.json')
        container = DataSetContainer()
        container.name = name
        self.write_processeddataset(container, processeddataset_uri)

    def create_data_processeddataset(self, data: ProcessedDataContainer, md_uri: str): 
        """create a new data metadata in the dataset
        
        The input data object must contain only the metadata (ie no
        uri and no md_uri). 
        This method generate the uri and the md_uri and save all the
        metadata

        Parameters
        ----------
        data
            metadata of the processed data to create 
        md_uri
            URI of the processed dataset    
        
        """    
        dataset_dir = md_file_path(md_uri)

        # create the data metadata
        data_md_file = os.path.join(dataset_dir, data.name, '.md.json')
        data.uri = os.path.join(dataset_dir, data.name, '.', data.format)
        self.write_processeddata(data, data_md_file)
        
        # add the data to the dataset
        dataset_container = self.read_processeddataset(md_uri)
        dataset_container.uris.append(data_md_file)
        self.write_processeddataset(dataset_container, md_uri)

    def read_experiment(self, md_uri: str) -> ExperimentContainer:
        if os.path.isfile(md_uri):
            metadata = self._read_json(md_uri)
            container = ExperimentContainer()
            container.name = metadata['information']['name']
            container.author = metadata['information']['author']
            container.date = metadata['information']['date']    
            container.rawdataset = absolute_path( metadata['rawdataset'], md_uri )
            for dataset in metadata['processeddatasets']:
                container.processeddatasets.append( absolute_path(dataset, md_uri))
            for tag in metadata['tags']:
                container.tags.append(tag)  
            return container  
        return ExperimentContainer

    def write_experiment(self, container:ExperimentContainer, md_uri:str):
        metadata = {}
        metadata['information'] = {}
        metadata['information']['name'] = container.name
        metadata['information']['author'] = container.author
        metadata['information']['date'] = container.date
        metadata['rawdataset'] = relative_path(container.rawdataset, md_uri)
        metadata['processeddatasets'] = []
        for dataset in container.processeddatasets:
            metadata['processeddatasets'].append( relative_path(dataset, md_uri) )
        metadata['tags'] = []    
        for tag in container.tags:
            metadata['tags'].append(tag)
        self._write_json(metadata, md_uri)     

    def create_experiment(self, container:ExperimentContainer, uri:str):

        # check the destination dir
        if not os.path.exists(uri):    
            raise MetadataServiceError('Cannot create Experiment: the destination directory does not exists')

        #create the experiment directory
        filtered_name = container.name.replace(' ', '')
        experiment_path = os.path.join(uri, filtered_name)
        if not os.path.exists(experiment_path):
            os.mkdir( experiment_path )    
        else:
            raise MetadataServiceError('Cannot create Experiment: the experiment directory already exists')

        # create an empty raw dataset
        rawdata_path = os.path.join(experiment_path, 'data')
        rawdataset_md_url = os.path.join(rawdata_path, 'rawdataset.md.json')
        container.rawdataset = rawdataset_md_url
        if os.path.exists(experiment_path):
            os.mkdir( rawdata_path )
        else:
            raise MetadataServiceError('Cannot create Experiment raw dataset: the experiment directory does not exists')

        rawdataset = DataSetContainer()
        rawdataset.name = 'data'    
        self.write_rawdataset(rawdataset, rawdataset_md_url)        

        # save the experiment.md.json metadata file
        md_uri = os.path.join(experiment_path, 'experiment.md.json')
        self.write_experiment(container, md_uri)
        return md_uri

    def import_data(self, data_path:str, rawdataset_uri:str, metadata: RawDataContainer, copy:bool):
        """Import a data to a raw dataset

        Parameters
        ----------
        data_path
            local path of the data to import
        rawdataset_uri
            URI of the raw dataset where the data will be imported
        metadata
            Metadata of the data to import
        copy
            True if the data is copied to the Experiment database
            False otherwise            

        """
        data_dir_path = os.path.dirname(rawdataset_uri)

        # create the new data uri
        data_base_name = os.path.basename(data_path)
        filtered_name = data_base_name.replace(' ', '')
        filtered_name, ext = os.path.splitext(filtered_name)
        md_uri = os.path.join(data_dir_path, filtered_name + '.md.json')

        # import data
        if copy:
            copied_data_path = os.path.join(data_dir_path, data_base_name)
            copyfile(data_path, copied_data_path)
            metadata.uri = copied_data_path
        else:    
            metadata.uri = data_path 
        self.write_rawdata(metadata, md_uri)    

        # add data to experiment RawDataSet
        rawdataset_container = self.read_rawdataset(rawdataset_uri)
        rawdataset_container.uris.append(md_uri)
        self.write_rawdataset(rawdataset_container, rawdataset_uri)
            
        return md_uri   

    def read_run(self, md_uri: str) -> RunContainer:
        if os.path.isfile(md_uri): 
            metadata = self._read_json(md_uri)
            container = RunContainer()
            container.process_name = metadata['process']['name']
            container.process_uri = metadata['process']['url']
            container.processeddataset = metadata['processeddataset']
            for input in metadata['inputs']:
                container.inputs.append(RunInputContainer(input['name'], input['dataset'], input['query'], input['origin_output_name']))
            for parameter in metadata['parameters']:
                container.parameters.append(RunParameterContainer(parameter['name'], parameter['value']))   
            return container
        return RunContainer()    

    def write_run(self, container: RunContainer, md_uri: str):
        metadata = dict()

        metadata['process'] = {}
        metadata['process']['name'] = container.process_name
        metadata['process']['url'] = container.process_uri
        metadata['processeddataset'] = container.processeddataset
        metadata['inputs'] = []
        for input in container.inputs:
            metadata['inputs'].append({'name': input.name, 'dataset': input.dataset, 'query': input.query, 'origin_output_name': input.origin_output_name})
        metadata['parameters'] = []
        for parameter in container.parameters:
            metadata['parameters'].append({'name': parameter.name, 'value': parameter.value })
        
        self._write_json(metadata, md_uri)    
