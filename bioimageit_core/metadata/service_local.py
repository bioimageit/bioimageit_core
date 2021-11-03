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
from pathlib import Path
import json
import re
from shutil import copyfile

from bioimageit_formats import FormatsAccess, formatsServices
from bioimageit_core.metadata.exceptions import MetadataServiceError
from bioimageit_core.metadata.containers import (METADATA_TYPE_RAW,
                                                 METADATA_TYPE_PROCESSED,
                                                 RawDataContainer,
                                                 ProcessedDataContainer,
                                                 ProcessedDataInputContainer,
                                                 DataSetContainer,
                                                 ExperimentContainer,
                                                 RunContainer,
                                                 RunInputContainer,
                                                 RunParameterContainer,
                                                 )


def md_file_path(md_uri: str) -> str:
    """get metadata file directory path

    Returns
    ----------
    str
        The name of the metadata file directory path

    """
    abspath = os.path.abspath(md_uri)
    return os.path.dirname(abspath)


def relative_path(file: str, reference_file: str):
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
    file = file.replace(separator + separator, separator)
    reference_file = reference_file.replace(separator + separator, separator)

    for i in range(len(file)):
        common_part = reference_file[0:i]
        if common_part not in file:
            break

    last_separator = common_part.rfind(separator)

    short_reference_file = reference_file[last_separator + 1:]

    number_of_sub_folder = short_reference_file.count(separator)
    short_file = file[last_separator + 1:]
    for i in range(number_of_sub_folder):
        short_file = '..' + separator + short_file

    return short_file


def absolute_path(file: str, reference_file: str):
    """convert file relative to reference_file into an absolute path

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
    canonical_path = reference_file[0: last_separator + 1]
    return simplify_path(canonical_path + file)


def simplify_path(path: str) -> str:
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
            for i in range(0, pos - 1):
                keep_folders.append(folders[i])
            for i in range(pos + 1, len(folders)):
                keep_folders.append(folders[i])
        else:
            found = False

    clean_path = ''
    for i in range(len(keep_folders)):
        clean_path += keep_folders[i]
        if i < len(keep_folders) - 1:
            clean_path += separator
    return clean_path


def normalize_path_sep(path: str) -> str:
    """Normalize the separators of a path
    
    Parameters
    ----------
    path: str
        Path to normalize
        
    Returns
    -------
    path normalized

    """
    p1 = path.replace('/', os.sep).replace('\\\\', os.sep)
    return p1


def to_unix_path(path: str) -> str:
    """Transform a path to unix path

    Parameters
    ----------
    path: str
        Path to unixify

    Returns
    -------
    Path with unix separator

    """
    return path.replace('\\\\', '/').replace('\\', '/')


class LocalMetadataServiceBuilder:
    """Service builder for the metadata service"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = LocalMetadataService()
        return self._instance


class LocalMetadataService:
    """Service for local metadata management"""

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
        """Read a raw data metadata from the database

        Parameters
        ----------
        md_uri
            URI of the data

        Returns
        -------
        a RawDataContainer that stores the raw data metadata

        """

        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri) and md_uri.endswith('.md.json'):
            metadata = self._read_json(md_uri)
            container = RawDataContainer()
            container.type = metadata['origin']['type']
            container.name = metadata['common']['name']
            container.author = metadata['common']['author']
            container.date = metadata['common']['date']
            container.format = metadata['common']['format']
            # copy the url if absolute, append md_uri path otherwise
            container.uri = absolute_path(normalize_path_sep(metadata['common']['url']), md_uri)
            if 'tags' in metadata:
                for key in metadata['tags']:
                    container.tags[key] = metadata['tags'][key]
            return container
        raise MetadataServiceError('Metadata file format not supported')

    def write_rawdata(self, container: RawDataContainer, md_uri: str):
        """Write a raw data metadata to the database

        Parameters
        ----------
        container
            object that contains the raw data metadata to write
        md_uri
            URI of the data

        """

        md_uri = os.path.abspath(md_uri)
        metadata = dict()

        metadata['origin'] = dict()
        metadata['origin']['type'] = METADATA_TYPE_RAW()

        metadata['common'] = dict()
        metadata['common']['name'] = container.name
        metadata['common']['author'] = container.author
        metadata['common']['date'] = container.date
        metadata['common']['format'] = container.format
        metadata['common']['url'] = to_unix_path(relative_path(container.uri, md_uri))

        metadata['tags'] = dict()
        for key in container.tags:
            metadata['tags'][key] = container.tags[key]

        self._write_json(metadata, md_uri)

    def read_processeddata(self, md_uri: str) -> ProcessedDataContainer:
        """Read a processed data metadata from the database

        Parameters
        ----------
        md_uri
            URI of the data

        Returns
        -------
        ProcessedDataContainer: object that contains the read processed
        data metadata

        """

        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri) and md_uri.endswith('.md.json'):
            metadata = self._read_json(md_uri)
            container = ProcessedDataContainer()
            container.name = metadata['common']['name']
            container.author = metadata['common']['author']
            container.date = metadata['common']['date']
            container.format = metadata['common']['format']
            container.uri = absolute_path(normalize_path_sep(metadata['common']['url']), md_uri)
            # origin run
            container.run_uri = absolute_path(normalize_path_sep(metadata['origin']['runurl']),
                                                                 md_uri)
            # origin input
            for input_ in metadata['origin']['inputs']:
                container.inputs.append(
                    ProcessedDataInputContainer(
                        input_['name'],
                        absolute_path(normalize_path_sep(input_['url']), md_uri),
                        input_['type'],
                    )
                )
            # origin
            if 'name' in metadata['origin']['output']:
                container.output['name'] = metadata['origin']['output']["name"]
            if 'label' in metadata['origin']['output']:
                container.output['label'] = \
                    metadata['origin']['output']['label']

            return container
        raise MetadataServiceError('Metadata file format not supported')

    def write_processeddata(self, container: ProcessedDataContainer,
                            md_uri: str):
        """Write a processed data metadata to the database

        Parameters
        ----------
        container
            object that contains the processed data metadata to write
        md_uri
            URI of the data

        """

        md_uri = os.path.abspath(md_uri)
        metadata = dict()
        # common
        metadata['common'] = dict()
        metadata['common']['name'] = container.name
        metadata['common']['author'] = container.author
        metadata['common']['date'] = container.date
        metadata['common']['format'] = container.format
        metadata['common']['url'] = to_unix_path(relative_path(container.uri, md_uri))
        # origin type
        metadata['origin'] = dict()
        metadata['origin']['type'] = METADATA_TYPE_PROCESSED()
        # run url
        metadata['origin']['runurl'] = to_unix_path(relative_path(container.run_uri, md_uri))
        # origin inputs
        metadata['origin']['inputs'] = list()
        for input_ in container.inputs:
            metadata['origin']['inputs'].append(
                {
                    'name': input_.name,
                    'url': to_unix_path(relative_path(input_.uri, md_uri)),
                    'type': input_.type,
                }
            )
        # origin ouput
        metadata['origin']['output'] = {
            'name': container.output['name'],
            'label': container.output['label'],
        }

        self._write_json(metadata, md_uri)

    def read_rawdataset(self, md_uri: str) -> DataSetContainer:
        """Read a raw dataset metadata from the database

        Parameters
        ----------
        md_uri
            URI of the dataset

        Returns
        -------
        DataSetContainer: object that contains the read dataset metadata

        """

        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri) and md_uri.endswith('.md.json'):
            metadata = self._read_json(md_uri)
            container = DataSetContainer()
            container.name = metadata['name']
            for uri in metadata['urls']:
                container.uris.append(absolute_path(normalize_path_sep(uri), md_uri))

            return container
        return DataSetContainer()

    def write_rawdataset(self, container: DataSetContainer, md_uri: str):
        """Write a raw dataset metadata to the database

        Parameters
        ----------
        container
            object that contains the raw dataset metadata to write
        md_uri
            URI of the dataset

        """

        md_uri = os.path.abspath(md_uri)
        metadata = dict()
        metadata['name'] = container.name
        metadata['urls'] = list()
        for uri in container.uris:
            metadata['urls'].append(to_unix_path(relative_path(uri, md_uri)))
        self._write_json(metadata, md_uri)

    def read_processeddataset(self, md_uri: str) -> DataSetContainer:
        """Read a processed dataset metadata from the database

        Parameters
        ----------
        md_uri
            URI of the dataset

        Returns
        -------
        DataSetContainer: object that contains the read dataset metadata

        """

        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri) and md_uri.endswith('.md.json'):
            metadata = self._read_json(md_uri)
            container = DataSetContainer()
            container.name = metadata['name']
            for uri in metadata['urls']:
                container.uris.append(absolute_path(normalize_path_sep(uri), md_uri))

            return container
        return DataSetContainer()

    def write_processeddataset(self, container: DataSetContainer, md_uri: str):
        """Write a processed dataset metadata to the database

        Parameters
        ----------
        container
            object that contains the processed dataset metadata to write

        md_uri
            URI of the dataset

        """

        md_uri = os.path.abspath(md_uri)
        metadata = dict()
        metadata['name'] = container.name
        metadata['urls'] = list()
        for uri in container.uris:
            metadata['urls'].append(to_unix_path(relative_path(uri, md_uri)))
        self._write_json(metadata, md_uri)

    def add_run_processeddataset(self, run: RunContainer, dataset_md_uri: str):
        """Add a run to a processed dataset

        Parameters
        ----------
        run
            Container of the Run metadata
        dataset_md_uri
            URI of the ProcessedDataset

        """

        # create run URI
        dataset_md_uri = os.path.abspath(dataset_md_uri)
        dataset_dir = md_file_path(dataset_md_uri)
        run_md_file_name = "run.md.json"
        runid_count = 0
        while os.path.isfile(os.path.join(dataset_dir, run_md_file_name)):
            runid_count += 1
            run_md_file_name = "run_" + str(runid_count) + ".md.json"
        run_uri = os.path.join(dataset_dir, run_md_file_name)

        # write run
        self.write_run(run, run_uri)
        return run_uri

    def create_processed_dataset(self, name: str, experiment_md_uri: str):
        """create a new processed dataset

        Parameters
        ----------
        name
            Name of the processed dataset
        experiment_md_uri
            URI of the experiment that contains the dataset

        """

        # create the dataset metadata
        experiment_md_uri = os.path.abspath(experiment_md_uri)
        experiment_dir = md_file_path(experiment_md_uri)
        dataset_dir = os.path.join(experiment_dir, name)
        if not os.path.isdir(dataset_dir):
            os.mkdir(dataset_dir)
        processeddataset_uri = os.path.join(
            experiment_dir, name, 'processeddataset.md.json'
        )
        container = DataSetContainer()
        container.name = name
        self.write_processeddataset(container, processeddataset_uri)

        print("experiment at:", experiment_md_uri)
        print("create the processed dataset at:", processeddataset_uri)

        # add the dataset to the experiment
        experiment_container = self.read_experiment(experiment_md_uri)
        experiment_container.processeddatasets.append(to_unix_path(processeddataset_uri))
        self.write_experiment(experiment_container, experiment_md_uri)

        return container, processeddataset_uri

    def create_data_processeddataset(self, data: ProcessedDataContainer,
                                     md_uri: str):
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

        md_uri = os.path.abspath(md_uri)
        dataset_dir = md_file_path(md_uri)

        # create the data metadata
        data_md_file = os.path.join(dataset_dir, data.name + '.md.json')
        ext = FormatsAccess.instance().get(data.format).extension
        data.uri = os.path.join(dataset_dir, data.name + '.' + ext)

        self.write_processeddata(data, data_md_file)

        # add the data to the dataset
        dataset_container = self.read_processeddataset(md_uri)
        dataset_container.uris.append(data_md_file)
        self.write_processeddataset(dataset_container, md_uri)

    def read_experiment(self, md_uri: str) -> ExperimentContainer:
        """Read an experiment metadata

        Parameters
        ----------
        md_uri
            URI of the experiment in the database

        Returns
        -------
        ExperimentContainer: object that contains an experiment metadata

        """

        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri):
            metadata = self._read_json(md_uri)
            container = ExperimentContainer()
            container.name = metadata['information']['name']
            container.author = metadata['information']['author']
            container.date = metadata['information']['date']
            container.rawdataset = absolute_path(normalize_path_sep(metadata['rawdataset']), md_uri)
            for dataset in metadata['processeddatasets']:
                container.processeddatasets.append(absolute_path(normalize_path_sep(dataset),
                                                                 md_uri))
            for tag in metadata['tags']:
                container.tags.append(tag)
            return container
        return ExperimentContainer()

    def write_experiment(self, container: ExperimentContainer, md_uri: str):
        """Write an experiment metadata to the database

        Parameters
        ----------
        container
            Object that contains an experiment metadata
        md_uri
            URI of the experiment in the database

        """

        md_uri = os.path.abspath(md_uri)
        metadata = dict()
        metadata['information'] = {}
        metadata['information']['name'] = container.name
        metadata['information']['author'] = container.author
        metadata['information']['date'] = container.date
        metadata['rawdataset'] = to_unix_path(relative_path(container.rawdataset, md_uri))
        metadata['processeddatasets'] = []
        for dataset in container.processeddatasets:
            metadata['processeddatasets'].append(to_unix_path(relative_path(dataset, md_uri)))
        metadata['tags'] = []
        for tag in container.tags:
            metadata['tags'].append(tag)
        self._write_json(metadata, md_uri)

    def create_experiment(self, container: ExperimentContainer, uri: str):
        """Create a new experiment metadata to the database

        Parameters
        ----------
        container
            Object that contains an experiment metadata
        uri
            URI of the experiment in the database

        """

        # check the destination dir
        uri = os.path.abspath(uri)
        if not os.path.exists(uri):
            raise MetadataServiceError(
                'Cannot create Experiment: the destination '
                'directory does not exists'
            )

        uri = os.path.abspath(uri)

        # create the experiment directory
        filtered_name = container.name.replace(' ', '')
        experiment_path = os.path.join(uri, filtered_name)
        if not os.path.exists(experiment_path):
            os.mkdir(experiment_path)
        else:
            raise MetadataServiceError(
                'Cannot create Experiment: the experiment '
                'directory already exists'
            )

        # create an empty raw dataset
        rawdata_path = os.path.join(experiment_path, 'data')
        rawdataset_md_url = os.path.join(rawdata_path, 'rawdataset.md.json')
        container.rawdataset = rawdataset_md_url
        if os.path.exists(experiment_path):
            os.mkdir(rawdata_path)
        else:
            raise MetadataServiceError(
                'Cannot create Experiment raw dataset: the experiment '
                'directory does not exists'
            )

        rawdataset = DataSetContainer()
        rawdataset.name = 'data'
        self.write_rawdataset(rawdataset, rawdataset_md_url)

        # save the experiment.md.json metadata file
        md_uri = os.path.join(experiment_path, 'experiment.md.json')
        self.write_experiment(container, md_uri)
        return md_uri

    def import_data(
        self,
        data_path: str,
        rawdataset_uri: str,
        metadata: RawDataContainer,
        copy: bool,
    ):
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

        rawdataset_uri = os.path.abspath(rawdataset_uri)
        data_dir_path = os.path.dirname(rawdataset_uri)

        # create the new data uri
        data_base_name = os.path.basename(data_path)
        filtered_name = data_base_name.replace(' ', '')
        filtered_name, ext = os.path.splitext(filtered_name)
        md_uri = os.path.join(data_dir_path, filtered_name + '.md.json')

        # import data
        if copy:
            print('import data with format:', metadata.format)
            format_service = formatsServices.get(metadata.format)
            files_to_copy = format_service.files(data_path)
            for file_ in files_to_copy:
                origin_base_name = os.path.basename(file_)
                destination_path = os.path.join(data_dir_path, origin_base_name)
                copyfile(file_, destination_path)
            metadata.uri = os.path.join(data_dir_path, data_base_name) # URI is main file    
        else:
            metadata.uri = data_path
        self.write_rawdata(metadata, md_uri)

        # add data to experiment RawDataSet
        rawdataset_container = self.read_rawdataset(rawdataset_uri)
        rawdataset_container.uris.append(md_uri)
        self.write_rawdataset(rawdataset_container, rawdataset_uri)

        return md_uri

    def read_run(self, md_uri: str) -> RunContainer:
        """Read a run metadata from the data base

        Parameters
        ----------
        md_uri
            URI of the run entry in the database

        Returns
        -------
        RunContainer: object containing the run metadata

        """

        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri):
            metadata = self._read_json(md_uri)
            container = RunContainer()
            container.process_name = metadata['process']['name']
            container.process_uri = normalize_path_sep(metadata['process']['url'])
            container.processeddataset = metadata['processeddataset']
            for input_ in metadata['inputs']:
                container.inputs.append(
                    RunInputContainer(
                        input_['name'],
                        input_['dataset'],
                        input_['query'],
                        input_['origin_output_name'],
                    )
                )
            for parameter in metadata['parameters']:
                container.parameters.append(
                    RunParameterContainer(parameter['name'], parameter['value'])
                )
            return container
        return RunContainer()

    def write_run(self, container: RunContainer, md_uri: str):
        """Write a run metadata to the data base

        Parameters
        ----------
        container
            Object containing the run metadata
        md_uri
            URI of the run entry in the database

        """

        metadata = dict()

        metadata['process'] = {}
        metadata['process']['name'] = container.process_name
        metadata['process']['url'] = to_unix_path(container.process_uri)
        metadata['processeddataset'] = container.processeddataset
        metadata['inputs'] = []
        for input_ in container.inputs:
            metadata['inputs'].append(
                {
                    'name': input_.name,
                    'dataset': input_.dataset,
                    'query': input_.query,
                    'origin_output_name': input_.origin_output_name,
                }
            )
        metadata['parameters'] = []
        for parameter in container.parameters:
            metadata['parameters'].append(
                {'name': parameter.name, 'value': parameter.value}
            )

        self._write_json(metadata, md_uri)

    def query_rep(self, repository_uri: str, filter_: str) -> list:
        """Query files in a repository

        Parameters
        ----------
        repository_uri
            URI of the repository
        filter_
            Regular expression to select a subset of file base on their names

        Returns
        -------
        The list of selected files

        """

        files = os.listdir(repository_uri)
        count = 0
        out_uris = []
        for file in files:
            count += 1
            r1 = re.compile(filter_)  # re.compile(r'\.tif$')
            if r1.search(file):
                out_uris.append(os.path.join(repository_uri, file))
        return out_uris

    def create_output_uri(
        self,
        output_rep_uri: str,
        output_name: str,
        format_: str,
        corresponding_input_uri: str,
    ) -> str:
        """Create the URI of an run output data file

        Parameters
        ----------
        output_rep_uri
            Output directory of the run
        output_name
            Output filename
        format_
            Output file format
        corresponding_input_uri
            URI of the origin input data

        Returns
        -------
        the created URI

        """

        if output_rep_uri == '':
            output_rep_uri = os.path.dirname(os.path.realpath(
                corresponding_input_uri))
        input_name = Path(corresponding_input_uri).stem
        output_uri = os.path.join(
            output_rep_uri, output_name + '_' + input_name + '.' + format_
        )
        if os.path.isfile(output_uri):
            os.remove(output_uri)
        return output_uri

    def workspace_experiments(self, workspace_uri: str):
        """Read the experiments in the user workspace

        Parameters
        ----------
        workspace_uri: str
            URI of the workspace

        Returns
        -------
        list of experiment containers    

        """
        if os.path.exists(workspace_uri):
            dirs = os.listdir(workspace_uri)
            experiments = []
            for dir in dirs:
                exp_path = os.path.join(workspace_uri, dir, 'experiment.md.json')
                if os.path.exists(exp_path):
                    experiments.append({'md_uri': exp_path, 'info': self.read_experiment(exp_path)})
            return experiments
        else:
            return []    
