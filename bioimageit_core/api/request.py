"""Main REST like API

This file implements the main BioImageIT API with using stateless operation like for a REST API

CLASSES
-------
Request

"""

import os
import re

from prettytable import PrettyTable

from bioimageit_core.core.observer import Observable, Observer
from bioimageit_core.core.config import ConfigAccess
from bioimageit_core.core.utils import format_date
from bioimageit_core.core.data_containers import METADATA_TYPE_RAW
from bioimageit_core.core.query import SearchContainer, query_list_single

from bioimageit_core.plugins.data_factory import metadataServices
from bioimageit_core.core.data_containers import Experiment
from bioimageit_core.plugins.tools_factory import toolsServices
from bioimageit_core.plugins.runners_factory import runnerServices
from bioimageit_core.core.exceptions import ConfigError, DataServiceError, DataQueryError


class Request(Observable):
    def __init__(self, config_file=''):
        super().__init__()

        self.add_observer(Observer())

        # load configuration
        self.config_file = config_file
        try:
            ConfigAccess(config_file)
        except ConfigError:
            self.notify_error(f'Cannot load the configuration from file: {config_file}')
            return

        # init services
        config = ConfigAccess.instance().config
        # metadata
        if 'metadata' in config and 'service' in config['metadata']:
            conf = config['metadata']
            try:
                self.data_service = metadataServices.get(conf["service"], **conf)
            except ConfigError as err:
                self.notify_error(str(err))
                return
        else:
            self.notify_error('The metadata service is not set in the configuration file')
            return

        # processes
        if 'process' in config and 'service' in config['process']:
            conf = config['process']
            try:
                self.process_service = toolsServices.get(config['process']["service"], **conf)
            except ConfigError as err:
                self.notify_error(str(err))
                return
        else:
            self.notify_error('The process service is not set in the configuration file')
            return

        # runner
        if 'runner' in config and 'service' in config['runner']:
            conf = config['runner']
            try:
                self.runner_service = runnerServices.get(conf["service"], **conf)
            except ConfigError as err:
                self.notify_error(str(err))
                return
        else:
            self.notify_error('The runner service is not set in the configuration file')
            return

    def create_experiment(self, name, author, date='now', keys=None, destination=''):
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
        try:
            return self.data_service.create_experiment(name, author, format_date(date),
                                                       keys, destination)
        except DataServiceError as err:
            self.notify_error(str(err))

    def get_experiment(self, uri):
        """Read an experiment from the database

        Parameters
        ----------
        uri: str
            URI of the experiment. For local use case, the URI is either the
            path of the experiment directory, or the path of the
            experiment.md.json file

        Returns
        -------
        Experiment container with the experiment metadata

        """
        try:
            return self.data_service.get_experiment(uri)
        except DataServiceError as err:
            self.notify_error(str(err))

    def update_experiment(self, experiment):
        """Write an experiment to the database

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata

        """
        try:
            self.data_service.update_experiment(experiment)
        except DataServiceError as err:
            self.notify_error(str(err))

    def set_key(self, experiment, key):
        """Set a new key to the experiment

        The experiment is automatically updated when a key is changed

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        key: str
            Key to set

        """
        try:
            experiment.set_key(key)
            self.data_service.update_experiment(experiment)
        except DataServiceError as err:
            self.notify_error(str(err))

    def set_keys(self, experiment, keys):
        """Set keys to the experiment

        The experiment is automatically updated when the keys are changed

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        keys: list
            List of keys

        """
        try:
            experiment.keys = keys
            self.data_service.update_experiment(experiment)
        except DataServiceError as err:
            self.notify_error(str(err))

    def import_data(self, experiment, data_path, name, author, format_,
                    date='now', key_value_pairs=dict, copy=True):
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
            Dictionary {key:value, key:value} of key-value pairs
        copy: bool
            True to copy the data to the Experiment database
            False otherwise
        Returns
        -------
        class RawData containing the metadata

        """
        try:
            return self.data_service.import_data(experiment, data_path, name, author,
                                                 format_, format_date(date), key_value_pairs, copy)
        except DataServiceError as err:
            self.notify_error(str(err))

    def import_dir(self, experiment, dir_uri, filter_, author, format_, date,
                   copy_data):
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
        copy_data: bool
            True to copy the data to the experiment, false otherwise. If the
            data are not copied, an absolute link to dir_uri is kept in the
            experiment metadata. The original data directory must then not be
            changed for the experiment to find the data.

        """
        files = os.listdir(dir_uri)
        count = 0
        r1 = re.compile(filter_)  # re.compile(r'\.tif$')
        for file in files:
            count += 1
            if r1.search(file):
                self.notify_progress(int(100 * count / len(files)), file)
                data_url = os.path.join(dir_uri, file)
                try:
                    self.data_service.import_data(experiment, data_url, file, author,
                                                  format_, format_date(date), {}, copy_data)
                except DataServiceError as err:
                    self.notify_error(str(err))
                    break

    def annotate_from_name(self, experiment, key, values):
        """Annotate an experiment raw data using raw data file names

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        key: str
            The name (or key) of the key to add to the data
        values: list
            List of possible values (str) for the key to find in the filename

        """
        experiment.set_key(key)
        self.update_experiment(experiment)
        _raw_dataset = self.get_raw_dataset(experiment)
        for uri in _raw_dataset.uris:
            _raw_data = self.get_raw_data(uri.md_uri)
            for value in values:
                if value in _raw_data.name:
                    _raw_data.set_key_value_pair(key, value)
                    self.update_raw_data(_raw_data)
                    break

    def annotate_using_separator(self, experiment, key, separator, value_position):
        """Annotate an experiment raw data files using file name and separator

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        key: str
            The name (or key) of the key to add to the data
        separator: str
            The character used as a separator in the filename (ex: _)
        value_position: int
            Position of the value to extract with respect to the separators

        """
        experiment.set_key(key)
        self.update_experiment(experiment)
        _raw_dataset = self.get_raw_dataset(experiment)
        for uri in _raw_dataset.uris:
            _raw_data = self.get_raw_data(uri.md_uri)
            basename = os.path.splitext(os.path.basename(_raw_data.uri))[0]
            split_name = basename.split(separator)
            value = ''
            if len(split_name) > value_position:
                value = split_name[value_position]
            _raw_data.set_key_value_pair(key, value)
            self.update_raw_data(_raw_data)

    def get_raw_data(self, uri):
        """Read a raw data from the database

        Parameters
        ----------
        uri: str
            URI if the raw data

        Returns
        -------
        RawData object containing the raw data metadata

        """
        try:
            return self.data_service.get_raw_data(uri)
        except DataServiceError as err:
            self.notify_error(str(err))

    def update_raw_data(self, raw_data):
        """Read a raw data from the database

        Parameters
        ----------
        raw_data: RawData
            Container with the raw data metadata

        """
        try:
            self.data_service.update_raw_data(raw_data)
        except DataServiceError as err:
            self.notify_error(str(err))

    def get_processed_data(self, uri):
        """Read a processed data from the database

        Parameters
        ----------
        uri: str
            URI if the processed data

        Returns
        -------
        ProcessedData object containing the raw data metadata

        """
        try:
            return self.data_service.get_processed_data(uri)
        except DataServiceError as err:
            self.notify_error(str(err))

    def update_processed_data(self, processed_data):
        """Read a processed data from the database

        Parameters
        ----------
        processed_data: ProcessedData
            Container with the processed_data metadata

        """
        try:
            self.data_service.update_processed_data(processed_data)
        except DataServiceError as err:
            self.notify_error(str(err))

    def get_dataset_from_uri(self, uri):
        """Read a dataset from the database using it URI

        Parameters
        ----------
        uri: str
            URI if the dataset

        Returns
        -------
        Dataset object containing the dataset metadata

        """
        try:
            return self.data_service.get_dataset(uri)
        except DataServiceError as err:
            self.notify_error(str(err))

    def update_dataset(self, dataset):
        """Read a processed data from the database

        Parameters
        ----------
        dataset: Dataset
            Container with the dataset metadata

        """
        try:
            self.data_service.update_dataset(dataset)
        except DataServiceError as err:
            self.notify_error(str(err))

    def get_raw_dataset(self, experiment):
        """Read the raw dataset from the database

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata

        Returns
        -------
        Dataset object containing the dataset metadata

        """
        try:
            return self.get_dataset_from_uri(experiment.raw_dataset.url)
        except DataQueryError as err:
            self.notify_error(str(err))

    def get_parent(self, processed_data):
        """Get the metadata of the parent data.
        The parent data can be a RawData or a ProcessedData
        depending on the process chain

        Parameters
        ----------
        processed_data: ProcessedData
            Container of the processed data URI

        Returns
        -------
        parent
            Parent data (RawData or ProcessedData)

        """
        if len(processed_data.inputs) > 0:
            if processed_data.inputs[0].type == METADATA_TYPE_RAW():
                return self.get_raw_data(processed_data.inputs[0].uri)
            else:
                return self.get_processed_data(processed_data.inputs[0].uri)
        return None

    def get_origin(self, processed_data):
        """Get the first metadata of the parent data.

        The origin data is a RawData. It is the first data that have
        been seen in the raw dataset

        Parameters
        ----------
        processed_data: ProcessedData
            Container of the processed data URI

        Returns
        -------
        the origin data in a RawData object

        """
        if len(processed_data.inputs) > 0:
            if processed_data.inputs[0].type == METADATA_TYPE_RAW():
                return self.get_raw_data(processed_data.inputs[0].uri)
            else:
                return self.get_origin(
                           self.get_processed_data(processed_data.inputs[0].uri))

    def get_dataset(self, experiment, name):
        """Query a dataset from it name

        Parameters
        ----------
        experiment: Experiment
            Object containing the experiment metadata
        name: str
            Name of the dataset to query

        Returns
        -------
        a Dataset containing the dataset metadata. None is return if the dataset
        is not found

        """
        if name == 'data':
            return self.get_dataset_from_uri(experiment.raw_dataset.url)
        else:
            for dataset_name in experiment.processed_datasets:
                p_dataset = self.get_dataset_from_uri(dataset_name.url)
                if p_dataset.name == name:
                    return p_dataset
        return None

    def get_data(self, dataset, query='', origin_output_name=''):
        """Query data from a dataset

        Parameters
        ----------
        dataset: Dataset
            Object containing the dataset metadata
        query
            String query with the key=value format.
        origin_output_name
            Name of the output origin (ex: -o) in the case of Processed Dataset
            search

        Returns
        -------
        list
            List of selected data (list of RawData or Processed Data objects)

        """
        if len(dataset.uris) < 1:
            return list()

        # search the dataset
        queries = re.split(' AND ', query)

        # initially all the raw data are selected
        #  first_data = self.get_raw_data(dataset.uris[0].md_uri)
        selected_list = []
        # raw dataset
        if dataset.name == 'data':
            for data_info in dataset.uris:
                data_container = self.get_raw_data(data_info.md_uri)
                selected_list.append(self._raw_data_to_search_container(
                    data_container))
        # processed dataset
        else:
            pre_list = []
            for data_info in dataset.uris:
                p_con = self.get_processed_data(data_info.md_uri)
                pre_list.append(self._processed_data_to_search_container(p_con))
            # remove the data where output origin is not the asked one
            if origin_output_name != '':
                for p_data in pre_list:
                    data = self.get_processed_data(p_data.uri())
                    if data.output["name"] == origin_output_name:
                        selected_list.append(p_data)
            else:
                selected_list = pre_list

        # run all the AND queries on the preselected dataset
        if query != '':
            for q in queries:
                try:
                    selected_list = query_list_single(selected_list, q)
                except DataQueryError as err:
                    self.notify_error(str(err))
                    return []

        # convert SearchContainer list to uri list
        out = []
        for d in selected_list:
            if dataset.name == 'data':
                out.append(self.get_raw_data(d.uri()))
            else:
                out.append(self.get_processed_data(d.uri()))
        return out

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
        try:
            return self.data_service.create_dataset(experiment, dataset_name)
        except DataServiceError as err:
            self.notify_error(str(err))

    def get_run(self, uri):
        """Read a run metadata from the data base

        Parameters
        ----------
        uri
            URI of the run entry in the database

        Returns
        -------
        Run: object containing the run metadata

        """
        try:
            return self.data_service.get_run(uri)
        except DataQueryError as err:
            self.notify_error(str(err))

    @staticmethod
    def _raw_data_to_search_container(raw_data):
        """convert a RawData to SearchContainer

        Parameters
        ----------
        raw_data: RawData
            Object containing the raw data

        Returns
        -------
        SearchContainer object

        """
        info = SearchContainer()
        info.data['name'] = raw_data.name
        info.data["uri"] = raw_data.md_uri
        info.data['key_value_pairs'] = raw_data.key_value_pairs
        return info

    def _processed_data_to_search_container(self, processed_data):
        """convert a ProcessedData to SearchContainer

        Parameters
        ----------
        processed_data: ProcessedData
            Object containing the processed_data

        Returns
        -------
        SearchContainer object

        """
        origin = self.get_origin(processed_data)
        if origin is not None:
            container = self._raw_data_to_search_container(origin)
        else:
            container = SearchContainer()
        container.data['name'] = processed_data.name
        container.data['uri'] = processed_data.md_uri
        container.data['uuid'] = processed_data.uuid
        return container

    def display_experiment(self, experiment, dataset='data'):
        """Display the Experiment metadata and the raw dataset content as a table in the console

        Parameters
        ----------
        experiment: Experiment
            Experiment to display
        dataset: str
            Name of the dataset to display

        """
        print("--------------------")
        print("Experiment: ")
        print("\tName: ", experiment.name)
        print("\tAuthor: ", experiment.author)
        print("\tCreated: ", experiment.date)
        print("\tKey-value pairs: ")
        for key in experiment.keys:
            print('\t\t-', key)
        print("\tDataSet: ", dataset)
        keys = experiment.keys
        t = PrettyTable(['Name'] + keys + ['Author', 'Created date'])
        if dataset == 'data':
            raw_dataset = self.get_dataset(experiment, dataset)
            for data_ in raw_dataset.uris:
                raw_data = self.get_raw_data(data_.md_uri)
                keys_values = []
                for key in keys:
                    keys_values.append(raw_data.key_value_pairs[key])
                t.add_row(
                    [raw_data.name]
                    + keys_values
                    + [raw_data.author, raw_data.date]
                )
        else:
            # TODO implement display processed dataset
            print('Display processed dataset not yet implemented')
        print(t)
