# -*- coding: utf-8 -*-
"""bioimageit_core local metadata service.

This module implements the local service for metadata
(Data, DataSet and Experiment) management.
This local service read/write and query metadata from a database
made od JSON file in the file system  

Classes
------- 
LocalMetadataServiceBuilder
LocalMetadataService

"""
import platform
import os
import os.path
from pathlib import Path
import json
import re
from shutil import copyfile
import subprocess

from bioimageit_formats import FormatsAccess, formatsServices

from bioimageit_core.core.config import ConfigAccess
from bioimageit_core.core.utils import generate_uuid
from bioimageit_core.core.exceptions import DataServiceError
from bioimageit_core.containers.data_containers import (METADATA_TYPE_RAW,
                                                        METADATA_TYPE_PROCESSED,
                                                        Container,
                                                        RawData,
                                                        ProcessedData,
                                                        ProcessedDataInputContainer,
                                                        Dataset,
                                                        Experiment,
                                                        Run,
                                                        RunInputContainer,
                                                        RunParameterContainer,
                                                        DatasetInfo,
                                                        )


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

    @staticmethod
    def _read_json(md_uri: str):
        """Read the metadata from the a json file"""
        if os.path.getsize(md_uri) > 0:
            with open(md_uri) as json_file:
                return json.load(json_file)

    @staticmethod
    def _write_json(metadata: dict, md_uri: str):
        """Write the metadata to the a json file"""
        with open(md_uri, 'w') as outfile:
            json.dump(metadata, outfile, indent=4)

    @staticmethod
    def md_file_path(md_uri):
        """get metadata file directory path
        Parameters
        ----------
        md_uri: str
            URI of the metadata
        Returns
        ----------
        str
            The name of the metadata file directory path
        """
        abspath = os.path.abspath(md_uri)
        return os.path.dirname(abspath)

    @staticmethod
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
        reference_file = reference_file.replace(separator + separator,
                                                separator)

        common_part = ''
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

    @staticmethod
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
        absolute path of file
        """
        if os.path.isfile(file):
            return os.path.abspath(file)

        separator = os.sep
        last_separator = reference_file.rfind(separator)
        canonical_path = reference_file[0: last_separator + 1]
        return LocalMetadataService.simplify_path(canonical_path + file)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def to_unix_path(path: str) -> str:
        """Transform a path to unix path
        Parameters
        ----------
        path: str
            Path to unix like
        Returns
        -------
        Path with unix separator
        """
        return path.replace('\\\\', '/').replace('\\', '/')

    def needs_cleanning(self):
        return False

    def create_experiment(self, name, author, date='now', keys=None,
                          destination=''):
        """Create a new experiment

        Parameters
        ----------
        name: str
            Name of the experiment
        author: str
            username of the experiment author
        date: str
            Creation date of the experiment
        keys: list
            List of keys used for the experiment vocabulary
        destination: str
            Destination where the experiment is created. It is a the path of the
            directory where the experiment will be created for local use case

        Returns
        -------
        Experiment container with the experiment metadata

        """
        if keys is None:
            keys = []
        container = Experiment()
        container.uuid = generate_uuid()
        container.name = name
        container.author = author
        container.date = date
        container.keys = keys

        # check the destination dir
        if destination == '':
            destination = ConfigAccess.instance().config['workspace']
        uri = os.path.abspath(destination)
        if not os.path.exists(uri):
            raise DataServiceError(
                'Cannot create Experiment: the destination '
                'directory does not exists'
            )

        uri = os.path.abspath(uri)

        # create the experiment directory
        filtered_name = name.replace(' ', '')
        experiment_path = os.path.join(uri, filtered_name)
        if not os.path.exists(experiment_path):
            os.mkdir(experiment_path)
        else:
            raise DataServiceError(
                'Cannot create Experiment: the experiment '
                'directory already exists'
            )

        # create an empty raw dataset
        raw_data_path = os.path.join(experiment_path, 'data')
        raw_dataset_md_url = os.path.join(raw_data_path, 'raw_dataset.md.json')
        if os.path.exists(experiment_path):
            os.mkdir(raw_data_path)
        else:
            raise DataServiceError(
                'Cannot create Experiment raw dataset: the experiment '
                'directory does not exists'
            )

        raw_dataset = Dataset()
        raw_dataset.uuid = generate_uuid()
        raw_dataset.md_uri = raw_dataset_md_url
        raw_dataset.name = 'data'
        self.update_dataset(raw_dataset)
        container.raw_dataset = DatasetInfo(raw_dataset.name, raw_dataset_md_url,
                                            raw_dataset.uuid)

        # save the experiment.md.json metadata file
        container.md_uri = os.path.join(experiment_path, 'experiment.md.json')
        self.update_experiment(container)
        return container

    def get_workspace_experiments(self, workspace_uri):
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
                    experiments.append({'md_uri': exp_path, 'info': self.get_experiment(exp_path)})
            return experiments
        else:
            return []  

    def get_experiment(self, md_uri):
        """Read an experiment from the database

        Parameters
        ----------
        md_uri: str
            URI of the experiment. For local use case, the URI is either the
            path of the experiment directory, or the path of the
            experiment.md.json file

        Returns
        -------
        Experiment container with the experiment metadata

        """
        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri):
            metadata = self._read_json(md_uri)
            container = Experiment()
            if 'uuid' in metadata:
                container.uuid = metadata['uuid']
            else:
                container.uuid = generate_uuid()       
            container.md_uri = md_uri
            container.name = metadata['information']['name']
            container.author = metadata['information']['author']
            container.date = metadata['information']['date']

            raw_dataset_url = LocalMetadataService.absolute_path(
                LocalMetadataService.normalize_path_sep(
                    metadata['raw_dataset']['url']), md_uri)
            container.raw_dataset = DatasetInfo(metadata['raw_dataset']['name'],
                                                raw_dataset_url,
                                                metadata['raw_dataset']['uuid'])
            for dataset in metadata['processed_datasets']:
                processed_dataset_url = LocalMetadataService.absolute_path(
                    LocalMetadataService.normalize_path_sep(
                        dataset['url']), md_uri)

                container.processed_datasets.append(
                    DatasetInfo(dataset['name'],
                                processed_dataset_url,
                                dataset['uuid']))
            for key in metadata['keys']:
                container.keys.append(key)
            return container
        raise DataServiceError('Cannot find the experiment metadata from the given URI')

    def update_experiment(self, experiment):
        """Write an experiment to the database

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata

        """
        md_uri_ = os.path.abspath(experiment.md_uri)
        metadata = dict()
        metadata['uuid'] = experiment.uuid
        metadata['information'] = {}
        metadata['information']['name'] = experiment.name
        metadata['information']['author'] = experiment.author
        metadata['information']['date'] = experiment.date

        tmp_url = LocalMetadataService.to_unix_path(
            LocalMetadataService.relative_path(experiment.raw_dataset.url,
                                               md_uri_))
        metadata['raw_dataset'] = {"name": experiment.raw_dataset.name,
                                   "url": tmp_url,
                                   "uuid": experiment.raw_dataset.uuid}
        metadata['processed_datasets'] = []
        for dataset in experiment.processed_datasets:
            tmp_url = LocalMetadataService.to_unix_path(
                          LocalMetadataService.relative_path(dataset.url, md_uri_))
            metadata['processed_datasets'].append(
                {"name": dataset.name, "url": tmp_url, "uuid": dataset.uuid}
                )
        metadata['keys'] = []
        for key in experiment.keys:
            metadata['keys'].append(key)
        self._write_json(metadata, md_uri_)

    def import_data(self, experiment, data_path, name, author, format_,
                    date='now', key_value_pairs=dict):
        """import one data to the experiment

        The data is imported to the raw dataset

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        data_path: str
            Path of the accessible data on your local computer
        name: str
            Name of the data
        author: str
            Person who created the data
        format_: str
            Format of the data (ex: tif)
        date: str
            Date when the data where created
        key_value_pairs: dict
            Dictionary {key:value, key:value} to annotate files

        Returns
        -------
        class RawData containing the metadata

        """
        raw_dataset_uri = os.path.abspath(experiment.raw_dataset.url)
        data_dir_path = os.path.dirname(raw_dataset_uri)

        # create the new data uri
        data_base_name = os.path.basename(data_path)
        filtered_name = data_base_name.replace(' ', '')
        filtered_name, ext = os.path.splitext(filtered_name)
        md_uri = os.path.join(data_dir_path, filtered_name + '.md.json')

        # create the container
        metadata = RawData()
        metadata.uuid = generate_uuid()
        metadata.md_uri = md_uri
        metadata.name = name
        metadata.author = author
        metadata.format = format_
        metadata.date = date
        metadata.key_value_pairs = key_value_pairs

        # import data
        # print('import data with format:', metadata.format)
        if metadata.format == 'bioformat':
            self._import_file_bioformat(raw_dataset_uri, data_path, data_dir_path, metadata.name,
                                        metadata.author, metadata.date)
        else:
            format_service = formatsServices.get(metadata.format)
            files_to_copy = format_service.files(data_path)
            for file_ in files_to_copy:
                origin_base_name = os.path.basename(file_)
                destination_path = os.path.join(data_dir_path, origin_base_name)
                copyfile(file_, destination_path)
            metadata.uri = os.path.join(data_dir_path, data_base_name)  # URI is main file
            self.update_raw_data(metadata)

            # add data to experiment RawDataSet
            raw_dataset_container = self.get_dataset(raw_dataset_uri)
            raw_dataset_container.uris.append(Container(md_uri=metadata.md_uri, uuid=metadata.uuid))
            self.update_dataset(raw_dataset_container)

        # add key-value pairs to experiment
        for key in key_value_pairs:
            experiment.set_key(key)
        self.update_experiment(experiment)

        return metadata

    def _import_file_bioformat(self, raw_dataset_uri, file_path, destination_dir, data_name, author,
                               date):
        fiji_exe = ConfigAccess.instance().get('fiji')
        cmd = f'{fiji_exe} --headless -macro bioimageit_convert.ijm "file,{file_path},' \
              f'{destination_dir},{data_name},{author},{date}"'
        print("import bioformat cmd:", cmd)
        if platform.system() == 'Windows':
            subprocess.run(cmd, check=True)
        else:
            subprocess.run(cmd, shell=True, executable='/bin/bash', check=True)

            # add data to raw dataset
        self._add_to_raw_dataset_bioformat(destination_dir, raw_dataset_uri)

    def _import_dir_bioformat(self, raw_dataset_uri, dir_uri, filter_, author, format_, date, directory_tag_key):
        fiji_exe = ConfigAccess.instance().get('fiji')

        raw_dataset_uri_ = os.path.abspath(raw_dataset_uri)
        data_dir_path = os.path.dirname(raw_dataset_uri_)

        cmd = f'{fiji_exe} --headless -macro bioimageit_convert.ijm "folder,{dir_uri},' \
              f'{data_dir_path},false,{filter_},{author},{date},{directory_tag_key}"'
        print("import bioformat cmd:", cmd)
        if platform.system() == 'Windows':
            subprocess.run(cmd, check=True)
        else:
            subprocess.run(cmd, shell=True, executable='/bin/bash', check=True)
        self._add_to_raw_dataset_bioformat(data_dir_path, raw_dataset_uri_)

    def _add_to_raw_dataset_bioformat(self, data_dir_path, raw_dataset_uri):
        # add the data to the dataset
        tmp_file = os.path.join(data_dir_path, 'tmp.txt')
        if os.path.isfile(tmp_file):
            raw_dataset = self.get_dataset(raw_dataset_uri)
            with open(tmp_file) as file:
                lines = file.readlines()
                for line in lines:
                    line = line.rstrip('\n')
                    raw_dataset.uris.append(os.path.join(data_dir_path, line))
                self.update_dataset(raw_dataset)
            os.remove(tmp_file)

    def import_dir(self, experiment, dir_uri, filter_, author, format_, date,
                   directory_tag_key='', observers=None):
        """Import data from a directory to the experiment

        This method import with or without copy data contained
        in a local folder into an experiment. Imported data are
        considered as RawData for the experiment

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        dir_uri: str
            URI of the directory containing the data to be imported
        filter_: str
            Regular expression to filter which files in the folder
            to import
        author: str
            Name of the person who created the data
        format_: str
            Format of the image (ex: tif)
        date: str
            Date when the data where created
        directory_tag_key
            If the string directory_tag_key is not empty, a new tag key entry with the
            key={directory_tag_key} and the value={the directory name}.
        observers: list
            List of observers to notify the progress

        """
        files = os.listdir(dir_uri)
        count = 0
        key_value_pairs = {}
        if directory_tag_key != '':
            key_value_pairs[directory_tag_key] = os.path.dirname(dir_uri)

        if format_ == 'bioformat':
            self._import_dir_bioformat(experiment.raw_dataset.md_uri, dir_uri, filter_,
                                       author, format_, date, directory_tag_key)
        else:
            for file in files:
                count += 1
                r1 = re.compile(filter_)
                if r1.search(file):
                    if observers is not None:
                        for obs in observers:
                            obs.notify_progress(int(100 * count / len(files)), file)
                    self.import_data(experiment, os.path.join(dir_uri, file), file, author,
                                     format_, date, key_value_pairs)

    def get_raw_data(self, md_uri):
        """Read a raw data from the database

        Parameters
        ----------
        md_uri: str
            URI if the raw data
        Returns
        -------
        RawData object containing the raw data metadata

        """
        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri) and md_uri.endswith('.md.json'):
            metadata = LocalMetadataService._read_json(md_uri)
            container = RawData()
            container.uuid = metadata['uuid']
            container.md_uri = md_uri
            container.type = metadata['origin']['type']
            container.name = metadata['common']['name']
            container.author = metadata['common']['author']
            container.date = metadata['common']['date']
            container.format = metadata['common']['format']
            # copy the url if absolute, append md_uri path otherwise
            container.uri = LocalMetadataService.absolute_path(
                LocalMetadataService.normalize_path_sep(
                    metadata['common']['url']), md_uri)

            # metadata
            if 'metadata' in metadata:
                container.metadata = metadata['metadata']

            # key_value_pairs
            if 'key_value_pairs' in metadata:
                for key in metadata['key_value_pairs']:
                    container.key_value_pairs[key] = metadata['key_value_pairs'][key]
            # read keys from the experiment
            experiment_uri = os.path.join(Path(Path(md_uri).parent).parent, 'experiment.md.json') 
            experiment = self.get_experiment(experiment_uri) 
            for key in experiment.keys:
                if 'key_value_pairs' in metadata:
                    if key not in metadata['key_value_pairs']:
                        container.key_value_pairs[key] = ''
            return container
        #raise DataServiceError(f'Metadata file format not supported: {md_uri}')
        return None

    def update_raw_data(self, raw_data):
        """Read a raw data from the database

        Parameters
        ----------
        raw_data: RawData
            Container with the raw data metadata

        """
        md_uri = os.path.abspath(raw_data.md_uri)
        metadata = dict()
        metadata['uuid'] = raw_data.uuid
        metadata['origin'] = dict()
        metadata['origin']['type'] = METADATA_TYPE_RAW

        metadata['common'] = dict()
        metadata['common']['name'] = raw_data.name
        metadata['common']['author'] = raw_data.author
        metadata['common']['date'] = raw_data.date
        metadata['common']['format'] = raw_data.format
        metadata['common']['url'] = LocalMetadataService.to_unix_path(
            LocalMetadataService.relative_path(raw_data.uri, md_uri))

        metadata['metadata'] = raw_data.metadata

        metadata['key_value_pairs'] = dict()
        for key in raw_data.key_value_pairs:
            metadata['key_value_pairs'][key] = raw_data.key_value_pairs[key]

        self._write_json(metadata, md_uri)

    def get_processed_data(self, md_uri):
        """Read a processed data from the database

        Parameters
        ----------
        md_uri: str
            URI if the processed data

        Returns
        -------
        ProcessedData object containing the raw data metadata

        """
        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri) and md_uri.endswith('.md.json'):
            metadata = self._read_json(md_uri)
            container = ProcessedData()
            container.uuid = metadata['uuid']
            container.md_uri = md_uri
            container.name = metadata['common']['name']
            container.author = metadata['common']['author']
            container.date = metadata['common']['date']
            container.format = metadata['common']['format']
            container.uri = LocalMetadataService.absolute_path(
                LocalMetadataService.normalize_path_sep(
                    metadata['common']['url']), md_uri)
            # origin run
            container.run = Container(LocalMetadataService.absolute_path(
                LocalMetadataService.normalize_path_sep(
                    metadata['origin']['run']["url"]), md_uri),
                metadata['origin']['run']["uuid"])
            # origin input
            for input_ in metadata['origin']['inputs']:
                container.inputs.append(
                    ProcessedDataInputContainer(
                        input_['name'],
                        LocalMetadataService.absolute_path(
                            LocalMetadataService.normalize_path_sep(
                                input_['url']), md_uri),
                        input_['uuid'],
                        input_['type'],
                    )
                )
            # origin output
            if 'name' in metadata['origin']['output']:
                container.output['name'] = metadata['origin']['output']["name"]
            if 'label' in metadata['origin']['output']:
                container.output['label'] = \
                    metadata['origin']['output']['label']

            return container
        #raise DataServiceError(f'Metadata file format not supported {md_uri}')
        return None

    def update_processed_data(self, processed_data):
        """Read a processed data from the database

        Parameters
        ----------
        processed_data: ProcessedData
            Container with the processed data metadata

        """
        md_uri = os.path.abspath(processed_data.md_uri)
        metadata = dict()
        metadata['uuid'] = processed_data.uuid
        # common
        metadata['common'] = dict()
        metadata['common']['name'] = processed_data.name
        metadata['common']['author'] = processed_data.author
        metadata['common']['date'] = processed_data.date
        metadata['common']['format'] = processed_data.format
        metadata['common']['url'] = LocalMetadataService.to_unix_path(
            LocalMetadataService.relative_path(processed_data.uri, md_uri))
        # origin type
        metadata['origin'] = dict()
        metadata['origin']['type'] = METADATA_TYPE_PROCESSED
        # run url
        run_url = LocalMetadataService.to_unix_path(
            LocalMetadataService.relative_path(processed_data.run.md_uri, md_uri))
        metadata['origin']['run'] = {"url": run_url,
                                     "uuid": processed_data.run.uuid}
        # origin inputs
        metadata['origin']['inputs'] = list()
        for input_ in processed_data.inputs:
            metadata['origin']['inputs'].append(
                {
                    'name': input_.name,
                    'url': LocalMetadataService.to_unix_path(
                        LocalMetadataService.relative_path(input_.uri, md_uri)),
                    'uuid': input_.uuid,
                    'type': input_.type,
                }
            )
        # origin output
        metadata['origin']['output'] = {
            'name': processed_data.output['name'],
            'label': processed_data.output['label'],
        }

        self._write_json(metadata, md_uri)

    def get_dataset(self, md_uri):
        """Read a dataset from the database using it URI

        Parameters
        ----------
        md_uri: str
            URI if the dataset

        Returns
        -------
        Dataset object containing the dataset metadata

        """
        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri) and md_uri.endswith('.md.json'):
            metadata = self._read_json(md_uri)
            container = Dataset()
            container.uuid = metadata["uuid"]
            container.md_uri = md_uri
            container.name = metadata['name']
            for uri in metadata['urls']:
                container.uris.append(
                    Container(LocalMetadataService.absolute_path(
                        LocalMetadataService.normalize_path_sep(uri['url']),
                        md_uri),
                        uri['uuid']))

            return container
        raise DataServiceError('Dataset not found')

    def update_dataset(self, dataset):
        """Read a processed data from the database

        Parameters
        ----------
        dataset: Dataset
            Container with the dataset metadata

        """
        md_uri = os.path.abspath(dataset.md_uri)
        metadata = dict()
        metadata['uuid'] = dataset.uuid
        metadata['name'] = dataset.name
        metadata['urls'] = list()
        for uri in dataset.uris:
            tmp_url = LocalMetadataService.to_unix_path(
                LocalMetadataService.relative_path(uri.md_uri, md_uri))
            metadata['urls'].append({"uuid": uri.uuid, 'url': tmp_url})
        self._write_json(metadata, md_uri)

    def create_dataset(self, experiment, dataset_name):
        """Create a processed dataset in an experiment

        Parameters
        ----------
        experiment: Experiment
            Object containing the experiment metadata
        dataset_name: str
            Name of the dataset

        Returns
        -------
        Dataset object containing the new dataset metadata

        """
        # create the dataset metadata
        experiment_md_uri = os.path.abspath(experiment.md_uri)
        experiment_dir = LocalMetadataService.md_file_path(experiment_md_uri)
        dataset_dir = os.path.join(experiment_dir, dataset_name)
        if not os.path.isdir(dataset_dir):
            os.mkdir(dataset_dir)
        processed_dataset_uri = os.path.join(
            experiment_dir, dataset_name, 'processed_dataset.md.json'
        )
        container = Dataset()
        container.uuid = generate_uuid()
        container.md_uri = processed_dataset_uri
        container.name = dataset_name
        self.update_dataset(container)

        # add the dataset to the experiment
        tmp_url = LocalMetadataService.to_unix_path(processed_dataset_uri)
        experiment.processed_datasets.append(
            DatasetInfo(dataset_name, tmp_url, container.uuid)
            )
        self.update_experiment(experiment)

        return container

    def create_run(self, dataset, run_info):
        """Create a new run metadata

        Parameters
        ----------
        dataset: Dataset
            Object of the dataset metadata
        run_info: Run
            Object containing the metadata of the run. md_uri is ignored and
            created automatically by this method

        Returns
        -------
        Run object with the metadata and the new created md_uri

        """
        # create run URI
        dataset_md_uri = os.path.abspath(dataset.md_uri)
        dataset_dir = LocalMetadataService.md_file_path(dataset_md_uri)
        run_md_file_name = "run.md.json"
        run_id_count = 0
        while os.path.isfile(os.path.join(dataset_dir, run_md_file_name)):
            run_id_count += 1
            run_md_file_name = "run_" + str(run_id_count) + ".md.json"
        run_uri = os.path.join(dataset_dir, run_md_file_name)

        # write run
        run_info.processed_dataset = dataset
        run_info.uuid = generate_uuid()
        run_info.md_uri = run_uri
        self._write_run(run_info)
        return run_info

    def get_dataset_runs(self, dataset):
        """Read the run metadata from a dataset

        Parameters
        ----------
        dataset: Dataset

        Returns
        -------
        List of Runs

        """
        run_uri = os.path.join(os.path.dirname(dataset.md_uri), 'run.md.json')
        return [self.get_run(run_uri)]


    def get_run(self, md_uri):
        """Read a run metadata from the data base

        Parameters
        ----------
        md_uri
            URI of the run entry in the database

        Returns
        -------
        Run: object containing the run metadata

        """
        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri):
            metadata = self._read_json(md_uri)
            container = Run()
            container.uuid = metadata['uuid']
            container.md_uri = md_uri
            container.process_name = metadata['process']['name']
            container.process_uri = LocalMetadataService.normalize_path_sep(
                metadata['process']['url'])
            container.processed_dataset = Container(
                LocalMetadataService.absolute_path(
                    LocalMetadataService.normalize_path_sep(
                        metadata['processed_dataset']['url']),
                    md_uri),
                metadata['processed_dataset']['uuid']
            )
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
        raise DataServiceError('Run not found')

    def _write_run(self, run):
        """Write a run metadata to the data base

        Parameters
        ----------
        run
            Object containing the run metadata

        """
        metadata = dict()
        metadata['uuid'] = run.uuid

        metadata['process'] = {}
        metadata['process']['name'] = run.process_name
        metadata['process']['url'] = LocalMetadataService.to_unix_path(
            run.process_uri)
        dataset_rel_url = LocalMetadataService.to_unix_path(
            LocalMetadataService.relative_path(run.processed_dataset.md_uri,
                                               run.md_uri))
        metadata['processed_dataset'] = {"uuid": run.processed_dataset.uuid,
                                         "url": dataset_rel_url}
        metadata['inputs'] = []
        for input_ in run.inputs:
            metadata['inputs'].append(
                {
                    'name': input_.name,
                    'dataset': input_.dataset,
                    'query': input_.query,
                    'origin_output_name': input_.origin_output_name,
                }
            )
        metadata['parameters'] = []
        for parameter in run.parameters:
            metadata['parameters'].append(
                {'name': parameter.name, 'value': parameter.value}
            )

        self._write_json(metadata, run.md_uri)

    def get_data_uri(self, data_container):
        return data_container.uri

    def create_data_uri(self, dataset, run, processed_data):
        """Create the URI of the new data

        Parameters
        ----------
        dataset: Dataset
            Object of the dataset metadata
        run: Run
            Metadata of the run
        processed_data: ProcessedData
            Object containing the new processed data. md_uri is ignored and
            created automatically by this method

        Returns
        -------
        ProcessedData object with the metadata and the new created md_uri

        """
        md_uri = os.path.abspath(dataset.md_uri)
        dataset_dir = LocalMetadataService.md_file_path(md_uri)

        extension = FormatsAccess.instance().get(processed_data.format).extension
        processed_data.uri = os.path.join(dataset_dir, f"{processed_data.name}.{extension}")
        return processed_data


    def create_data(self, dataset, run, processed_data):
        """Create a new processed data for a given dataset

        Parameters
        ----------
        dataset: Dataset
            Object of the dataset metadata
        run: Run
            Metadata of the run
        processed_data: ProcessedData
            Object containing the new processed data. md_uri is ignored and
            created automatically by this method

        Returns
        -------
        ProcessedData object with the metadata and the new created md_uri

        """
        md_uri = os.path.abspath(dataset.md_uri)
        dataset_dir = LocalMetadataService.md_file_path(md_uri)

        # create the data metadata
        data_md_file = os.path.join(dataset_dir, processed_data.name + '.md.json')
        processed_data.uuid = generate_uuid()
        processed_data.md_uri = data_md_file
        extension = FormatsAccess.instance().get(processed_data.format).extension
        processed_data.uri = os.path.join(dataset_dir, f"{processed_data.name}.{extension}")

        processed_data.run = run

        self.update_processed_data(processed_data)

        # add the data to the dataset
        dataset.uris.append(Container(data_md_file, processed_data.uuid))
        self.update_dataset(dataset)

        return processed_data

    def download_data(self, md_uri, destination_file_uri):
        if destination_file_uri == '':
            raw_data = self.get_raw_data(md_uri)
            return raw_data.uri
        return destination_file_uri        