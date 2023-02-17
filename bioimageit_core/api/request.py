"""Main REST like API

This file implements the main BioImageIT API with using stateless operation like for a REST API

CLASSES
-------
Request

"""

import os
import re
import json
import shlex
from bioimageit_core.containers.pipeline_containers import Pipeline
from prettytable import PrettyTable

from bioimageit_formats import FormatsAccess, FormatKeyNotFoundError, FormatDatabaseError

from bioimageit_core.core.observer import Observable, Observer
from bioimageit_core.core.config import ConfigAccess
from bioimageit_core.core.utils import format_date
from bioimageit_core.containers.data_containers import (METADATA_TYPE_RAW, ProcessedData,
                                                        Dataset, Run, ProcessedDataInputContainer)
from bioimageit_core.containers.tools_containers import Tool
from bioimageit_core.core.query import SearchContainer, query_list_single
from bioimageit_core.core.log_observer import LogObserver

from bioimageit_core.plugins.data_factory import metadataServices
from bioimageit_core.containers.data_containers import Experiment
from bioimageit_core.plugins.tools_factory import toolsServices
from bioimageit_core.plugins.runners_factory import runnerServices
from bioimageit_core.core.exceptions import (ConfigError, DataServiceError, DataQueryError,
                                             ToolsServiceError, ToolNotFoundError, RunnerExecError)
from bioimageit_core.containers.runners_containers import Job                                             


class APIAccess:
    """Singleton to access the BioImageIT API (Request)

    Parameters
    ----------
    config_file
        JSON file where the config is stored

    Raises
    ------
    Exception: if multiple instantiation of the Config is tried

    """

    __instance = None

    def __init__(self, config_file: str):
        """ Virtually private constructor. """
        if APIAccess.__instance is not None:
            raise Exception("ConfigManager can be initialized only once!")
        else:
            APIAccess.__instance = Request(config_file)

    @staticmethod
    def instance(config_file='', debug=True):
        """ Static access method to the Config. """
        if APIAccess.__instance is None:
            APIAccess.__instance = Request(config_file, debug)
        return APIAccess.__instance


class Request(Observable):
    def __init__(self, config_file='', debug=True, log=True):
        super().__init__()

        # cmd observers
        self.add_observer(Observer(debug))

        # Declare services
        self.data_service = None
        self.tools_service = None
        self.runner_service = None

        # load configuration
        self.config_file = config_file
        try:
            ConfigAccess.instance(config_file)
        except ConfigError:
            self.notify_error(f'Cannot load the configuration from file: {config_file}')
            return

        # log observer
        self.log_observer = None
        if log:
            config = ConfigAccess.instance().config
            if 'log_dir' in config and os.path.exists(config['log_dir']):
                self.log_observer = LogObserver(config['log_dir'])
                self.add_observer(self.log_observer)

    def add_log_observer(self, log_dir, log_file_id):
        self.log_observer = LogObserver(log_dir, log_file_id)
        self.add_observer(self.log_observer)           

    def connect(self, init_format=True, init_metadata=True, init_process=True, init_runner=True):
        # init services
        config = ConfigAccess.instance().config
        # formats
        if init_format:
            if 'formats' in config and 'file' in config['formats']:
                try:
                    FormatsAccess(config['formats']['file'])
                except FormatDatabaseError as err:
                    self.notify_error(str(err))
        # metadata
        if init_metadata:
            if 'metadata' in config and 'service' in config['metadata']:
                conf = config['metadata'].copy()
                service_name = conf["service"]
                conf.pop("service")
                try:
                    self.data_service = metadataServices.get(service_name, **conf)
                except ConfigError as err:
                    self.notify_error(str(err))
                    return
                except DataServiceError as err:
                    self.notify_error(str(err))
                    return    
            else:
                self.notify_error('The metadata service is not set in the configuration file')
                return

        # processes
        if init_process:
            if 'process' in config and 'service' in config['process']:
                conf = config['process'].copy()
                service_name = conf["service"]
                conf.pop("service")
                try:
                    self.tools_service = toolsServices.get(service_name, **conf)
                except ConfigError as err:
                    self.notify_error(str(err))
                    return
                except ToolsServiceError as err:   
                    self.notify_error(str(err)) 
                    return
            else:
                self.notify_error('The process service is not set in the configuration file')
                return

        # runner
        if init_runner:
            if 'runner' in config and 'service' in config['runner']:
                conf = config['runner'].copy()
                service_name = conf["service"]
                conf.pop("service")
                try:
                    self.runner_service = runnerServices.get(service_name, **conf)
                    for obs in self._observers:
                        self.runner_service.add_observer(obs)
                except ConfigError as err:
                    self.notify_error(str(err))
                    return
            else:
                self.notify_error('The runner service is not set in the configuration file')
                return

    def create_experiment(self, name, author='', date='now', keys=None, destination=''):
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
            if author == '':
                author = ConfigAccess.instance().config['user']
            return self.data_service.create_experiment(name, author, format_date(date),
                                                       keys, destination)
        except DataServiceError as err:
            self.notify_error(str(err))

    def get_workspace_experiments(self):
        """Get the list of experiment in the use workspace """

        config = ConfigAccess.instance().config
        wrokspace_dir = ''
        if 'workspace' in config:
            wrokspace_dir = config['workspace']      
        else:
            self.notify_error('No workspace specified in the configuration file')         

        try:
            return self.data_service.get_workspace_experiments(wrokspace_dir)
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
            Dictionary {key:value, key:value} of key-value pairs
        Returns
        -------
        class RawData containing the metadata

        """
        try:
            return self.data_service.import_data(experiment, data_path, name, author,
                                                 format_, format_date(date), key_value_pairs)
        except DataServiceError as err:
            self.notify_error(str(err))
        except ValueError as err:
            self.notify_error(f"The format {str(err)} is not recognised")

    def import_dir(self, experiment, dir_uri, filter_, author='', format_='imagetiff', date='now',
                   directory_tag_key=''):
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

        """
        try:
            if author == '':
                author = ConfigAccess.instance().config['user']['name']
            return self.data_service.import_dir(experiment, dir_uri, filter_, author,
                                                format_, format_date(date), directory_tag_key)
        except DataServiceError as err:
            self.notify_error(str(err))
        except ValueError as err:
            self.notify_error(f"The format {str(err)} is not recognised")

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
            basename = os.path.splitext(_raw_data.name)[0] #os.path.splitext(os.path.basename(_raw_data.uri))[0]
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
            if processed_data.inputs[0].type == METADATA_TYPE_RAW:
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
        if processed_data is not None and len(processed_data.inputs) > 0:
            if processed_data.inputs[0].type == METADATA_TYPE_RAW:
                return self.get_raw_data(processed_data.inputs[0].uri)
            else:
                return self.get_origin(
                           self.get_processed_data(processed_data.inputs[0].uri))

    def is_dataset(self, experiment, name):
        """Check if a dataset exists
        
        Parameters
        ----------
        experiment: Experiment
            Object containing the experiment metadata
        name: str
            Name of the dataset to query

        Returns
        -------
        True if exists, false otherwise
        
        """
        if name == 'data':
            return True
        else:
            for dataset in experiment.processed_datasets:
                if dataset.name == name:
                    return True    
        return False            

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

    def query(self, experiment, dataset_name, query='', origin_output_name=''):
        """Query data from a dataset

        Parameters
        ----------
        experiment: Experiment
            Experiment to query on
        dataset_name: str
            unique name of the dataset to query
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
        dataset = self.get_dataset(experiment, name=dataset_name)
        return self.get_data(dataset, query, origin_output_name)

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
        return self.data_service.create_run(dataset, run_info)

    def get_dataset_runs(self, dataset):
        """Read the run metadata from a dataset

        Parameters
        ----------
        dataset: Dataset

        Returns
        -------
        List of Runs

        """
        try:
            return self.data_service.get_dataset_runs(dataset)
        except DataQueryError as err:
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
        return self.data_service.create_data(dataset, run, processed_data)

    def search_tool(self, keyword: str = '', print_=False):
        """Search a tool using a keyword in the database

        This method print the list of funded processed

        Parameters
        ----------
        keyword
            Keyword to search in the database
        print_: bool
            True to print tools in a PrettyTable, False otherwise

        Returns
        -------
        The list of tools        

        """
        try:
            plist = self.tools_service.search(keyword)
            if print_:
                x = PrettyTable()
                x.field_names = ["UUID", "Name", "Version", "Type"]
                for tool in plist:
                    type_ = 'sequential'
                    if tool.type != '':
                        type_ = tool.type
                    x.add_row([tool.id, tool.name, tool.version, type_])
                print(x)
            return plist
        except ToolsServiceError as err:
            self.notify_error(str(err))
        except ToolNotFoundError as err:
            self.notify_error(str(err))

    def get_pipeline(self, uri: str) -> Pipeline:
        """Read a pipeline

        Parameters
        ----------
        uri: str
            URI of the pipeline 

        Returns
        -------
        Instance of Pipeline

        """
        try:
            return self.tools_service.get_pipeline(uri)
        except ToolsServiceError as err:
            self.notify_error(f'{uri}: str(err)')
        except ToolNotFoundError as err:
            self.notify_error(f'{uri}: str(err)')

    def get_tool_from_uri(self, uri: str) -> Tool:
        """Read a tool in the database form it URI
        
        Parameters
        ----------
        uri
            URI of the tool (address of the XML file)

        Returns
        -------
        An instance of Tool

        
        """
        try:
            return self.tools_service.read_tool(uri)
        except ToolsServiceError as err:
            self.notify_error(f'{uri}: str(err)')
        except ToolNotFoundError as err:
            self.notify_error(f'{uri}: str(err)')

    def get_tool(self, name: str) -> Tool:
        """get a process by name

        Parameters
        ----------
        name
            Fullname of the tool ({name}_v{version})

        Returns
        -------
        An instance of Tool

        """
        try:
            return self.tools_service.get_tool(name)
        except ToolsServiceError as err:
            self.notify_error(str(err))
        except ToolNotFoundError as err:
            self.notify_error(str(err))

    def get_categories(self, parent: str) -> list:
        """Get a list of categories for a given parent category

        Parameters
        ----------
        parent
            ID of the parent category

        """
        try:
            return self.tools_service.get_categories(parent)
        except ToolsServiceError as err:
            self.notify_error(str(err))
        except ToolNotFoundError as err:
            self.notify_error(str(err))

    def get_category_tools(self, category: str) -> list:
        """Get the list of tools with the given category

        Parameters
        ----------
        category
            ID of the category

        """
        try:
            return self.tools_service.get_category_tools(category)
        except ToolsServiceError as err:
            self.notify_error(str(err))
        except ToolNotFoundError as err:
            self.notify_error(str(err))

    def export_tools_to_json(self, destination: str):
        """Export the database into a JSON file

        Parameters
        ----------
        destination
            URI of the json file where the database is saved

        """
        database = self.tools_service.get_tools_database()
        d_dict = dict()
        for elem in database:
            d_dict[elem] = database[elem].to_dict()
        with open(destination, 'w') as outfile:
            json.dump(d_dict, outfile, indent=4)

    def _prepare_command(self, tool, parameters):
        """prepare a command line from user inputs

        Parameters
        ----------
        tool: Tool
            Information of the tool to run
        parameters: dict
            Dictionary of i/o and parameters key-values

        """
        # 1. check inputs
        for input_arg in tool.inputs:
            if input_arg.name not in parameters and input_arg.type:
                self.notify_warning(
                    f'Warning (Runner): cannot find the input: {input_arg.name} will use the '
                    f'default value: {input_arg.default_value} '
                )
                input_arg.value = input_arg.default_value
        for output_arg in tool.outputs:
            if output_arg.name not in parameters:
                self.notify_warning(
                    'Warning (Runner): cannot find the output: {output_arg.name} '
                    'will use the default value: {output_arg.default_value}'
                )
                output_arg.value = output_arg.default_value
        # 2. exec
        # 2.1- get the parameters values
        for key in parameters:
            for input_arg in tool.inputs:
                if input_arg.name == key and input_arg.type:
                    input_arg.value = parameters[key]
            for output_arg in tool.outputs:
                if output_arg.name == key:
                    output_arg.value = parameters[key]
        # 2.2.1. build the command line
        cmd = tool.command
        for input_arg in tool.inputs:
            cmd = cmd.replace("${" + input_arg.name + "}",
                              "'" + str(input_arg.value) + "'")
            input_arg_name_simple = input_arg.name.replace("-", "")
            cmd = cmd.replace("${" + input_arg_name_simple + "}",
                              "'" + str(input_arg.value) + "'")
        for output_arg in tool.outputs:
            cmd = cmd.replace("${" + output_arg.name + "}",
                              "'" + str(output_arg.value) + "'")
        # 2.2.2. replace the command variables
        cmd = self._replace_env_variables(tool, cmd)
        cmd = cmd.replace('/', os.sep)
        # 2.3. exec
        args = shlex.split(cmd)
        return args

    def exec(self, tool, **kwargs):
        """Process one data from it uri

        This method will process a data from the file directly and no metadata will be managed.
        This method is provided only for developers who needs to manage manually the metadata, or
        for people who only want to try a process without tracking the results and metadata.

        Parameters
        ----------
        tool: Tool
            Container of the tool information
        kwargs:
            Dictionary of the tool inputs, outputs and parameters.
            Ex: {"i": "image.tif", "o": result.tif, "threshold": 128}

        """
        args = self._prepare_command(tool, kwargs)
        job_id = self.new_job()
        self.notify(f'Start job{job_id}')
        try:
            self.runner_service.set_up(tool, job_id)
            self.runner_service.exec(tool, args, job_id)
            self.runner_service.tear_down(tool, job_id)
        except RunnerExecError as err:
            self.notify_error(str(err), job_id)
        self.notify(f'Finished job{job_id}')

    @staticmethod
    def _replace_env_variables(tool, cmd) -> str:
        xml_root_path = os.path.dirname(os.path.abspath(tool.uri))
        cmd_out = cmd.replace("$__tool_directory__", xml_root_path)
        if 'fiji' in ConfigAccess.instance().config:
            cmd_out = cmd_out.replace("$__fiji__", ConfigAccess.instance().config['fiji'])
        config = ConfigAccess.instance()
        if config.is_key('env'):
            for element in config.get('env'):
                cmd_out = cmd_out.replace(
                    "${" + element["name"] + "}", element["value"]
                )
        return cmd_out

    def download_data(self, md_uri):
        """Download the data in a tmp file if remote database

        Parameters
        ----------
        md_uri: str
            Unique uri of the image

        Returns
        -------
        The local path of the image    

        """
        try:
            return self.data_service.download_data(md_uri, '')
        except DataServiceError as err:
            self.notify_error(str(err))    

    def view_data(self, md_uri):
        try:
            return self.data_service.view_data(md_uri)
        except DataServiceError as err:
            self.notify_error(str(err)) 


    def run(self, job):
        """Run a BioImageIT job

        A BioImageIT job is a run of a processing tool in a database. The data to process are
        selected in the database using a specified request, and the results are automatically
        saved in a new dataset of the database. All the metadata of the job (tool, request,
        parameters) are also saved in the database.

        Parameters
        ----------
        job: Job
            Container of the job information

        """
        if job.tool.type == "merge":
            self._run_job_merged(job)
        else:
            self._run_job_sequence(job)
        return self.get_experiment(job.experiment.md_uri)

    def _query_inputs(self, job):
        if len(job.inputs.inputs) == 0:
            raise RunnerExecError('No input data specified')

        input_data = dict()
        data_count = 0
        for i, job_input in enumerate(job.inputs.inputs):
            input_data[i] = self.get_data(
                self.get_dataset(job.experiment, job_input.dataset),
                job_input.query,
                job_input.origin_output_name
            )
            #print([d.name for d in input_data[i]])
            #print('')
            if i == 0:
                data_count = len(input_data[i])
            else:
                if len(input_data[i]) != data_count:
                    raise RunnerExecError(
                        "Input dataset queries does not "
                        "have the same number of data"
                    )
        return [input_data, data_count]

    def _run_job_sequence(self, job):
        """Run the process in a sequence

        This is the main function that run the process on the experiment data. The sequence means
        that all the queried data are processed independently with the same tool and the same
        parameters.

        Parameters
        ----------
        job: Job
            Container of the job information
        """
        # 1- Query all the input data and verify that the size are equal, if not return an error
        input_data, data_count = self._query_inputs(job)

        # 2- Create the ProcessedDataSet
        processed_dataset = self.create_dataset(job.experiment, job.output_dataset_name)

        # 3- Create run metadata
        run = Run()
        run.process_name = job.tool.fullname()
        run.process_uri = job.tool.uri
        for t, input_ in enumerate(job.inputs.inputs):
            run.add_input(input_.name, input_.dataset,
                          input_.query, input_.origin_output_name)
        for key, value in job.parameters.items():
            run.add_parameter(key, value)
        run = self.create_run(processed_dataset, run)  # save to database

        # 4- loop over the input data to run processing
        job_id = self.new_job()
        self.notify(f'Start job{job_id}')
        self.runner_service.set_up(job.tool, job_id)
        for i in range(data_count):
            cmd = job.tool.command
            data_info_zero = self.get_raw_data(input_data[0][i].md_uri)
            # 4.0- notify observers
            self.notify_progress(int(100 * i / data_count),
                                 f"Process {data_info_zero.name}", job_id)
            # 4.1- Parse IO
            # get the input arguments
            inputs_metadata = {}
            local_files = []
            for n, input_ in enumerate(job.inputs.inputs):
                # input data can be a processedData but we only read the common metadata
                data_info = self.get_raw_data(input_data[n][i].md_uri)
                data_uri = self.data_service.get_data_uri(data_info)
                # data_info.uri
                self.data_service.download_data(data_info.md_uri, data_uri)
                local_files.append(data_uri)
                cmd = cmd.replace("${" + input_.name + "}", data_uri)
                inputs_metadata[input_.name] = data_info
            # get the params arguments
            for key, value in job.parameters.items():
                cmd = cmd.replace("${" + key + "}", value)
            # setup outputs
            processed_data_list = []
            for output in job.tool.outputs:
                # output metadata
                processed_data = ProcessedData()
                processed_data.set_info(name=output.name + "_" + os.path.splitext(data_info_zero.name)[0],
                                        author=ConfigAccess.instance().get('user')['name'],
                                        date='now', format_=output.type, url="")
                for id_, data_ in inputs_metadata.items():
                    processed_data.add_input(id_=id_, data=data_)
                processed_data.set_output(id_=output.name, label=output.description)
                processed_data = self.data_service.create_data_uri(processed_dataset, run, processed_data)
                # args
                local_files.append(processed_data.uri)
                cmd = cmd.replace("${" + output.name + "}", processed_data.uri)
                processed_data_list.append(processed_data)
            # 4.2- exec
            try:
                cmd = self._replace_env_variables(job.tool, cmd)
                cmd = cmd.replace('/', os.sep)
                self.runner_service.exec(job.tool, shlex.split(cmd), job_id)
            except RunnerExecError as err:
                self.runner_service.tear_down(job.tool, job_id)
                self.notify_error(str(err), job_id)
            # 4.3- create the output data
            for processed_data in processed_data_list:
                # save the metadata and create its md_uri and uri
                try:
                    processed_data = self.create_data(processed_dataset, run, processed_data)
                except FormatKeyNotFoundError as err:
                    self.notify_error(str(err), job_id)
                    return

            if self.data_service.needs_cleanning():
                for file in local_files:
                    if os.path.exists(file):
                        os.remove(file)            

        # 4.0- notify observers
        self.runner_service.tear_down(job.tool, job_id)
        self.notify_progress(100, 'done', job_id)
        self.notify(f'Finished job{job_id}')

    def _run_job_merged(self, job):
        """Run the process that merge txt number inputs

         This is the main function that run the process on the experiment data

         """
        self.notify_progress(0, 'start')

        # 1- Query all the input data and verify that the size
        # are equal, if not raise an exception
        input_data, data_count = self._query_inputs(job)

        # 2- Create the ProcessedDataSet
        processed_dataset = self.create_dataset(job.experiment, job.output_dataset_name)

        # 3- Create run
        run = Run()
        run.process_name = job.tool.fullname()
        run.process_uri = job.tool.uri
        for input_ in job.inputs.inputs:
            run.add_input(input_.name, input_.dataset, input_.query,
                          input_.origin_output_name)
        for key, value in job.parameters.items():
            run.add_parameter(key, value)
        run = self.create_run(processed_dataset, run)  # save to database

        # 4- merge Inputs
        inputs_values = [0.0 for i in range(job.inputs.count())]
        for n, input_ in enumerate(job.inputs.inputs):
            inputs_values[n] = list()
            for i in range(data_count):
                data_info = self.get_raw_data(input_data[n][i].md_uri)
                if data_info.format == "numbercsv":
                    with open(data_info.uri, 'r') as file:
                        value = file.read().replace('\n', '').replace(' ', '')
                        inputs_values[n].append(float(value))
                else:
                    self.notify_error('run merge can use only number datatype')

        # 5- save data in tmp files in the processed dataset dir
        tmp_inputs_files = [0 for i in range(job.inputs.count())]
        processed_data_dir = processed_dataset.md_uri.replace(
            "processed_dataset.md.json", ""
        )
        for n, input_ in enumerate(job.inputs.inputs):
            tmp_inputs_files[n] = os.path.join(
                processed_data_dir, input_.name + '.csv'
            )
            f = open(tmp_inputs_files[n], 'w')
            for i in range(len(inputs_values[n])):
                value = str(inputs_values[n][i])
                if i < len(inputs_values[n]) - 1:
                    f.write(value + ",")
                else:
                    f.write(value)
            f.close()

        # 6- create input metadata for output .md.json
        inputs_metadata = []
        for n in range(len(tmp_inputs_files)):
            inp_metadata = ProcessedDataInputContainer()
            inp_metadata.name = job.inputs.inputs[n].name
            inp_metadata.uri = tmp_inputs_files[n]
            inp_metadata.type = 'txt'
            inputs_metadata.append(inp_metadata)

        # 7- run process on generated files
        cmd = job.tool.command

        # 7.1- inputs
        for n, input_ in enumerate(job.inputs.inputs):
            cmd = cmd.replace("${" + input_.name + "}", tmp_inputs_files[n])

        # 7.2- params
        for key, value in job.parameters.items():
            cmd = cmd.replace("${" + key + "}", value)

        # 4.3- outputs
        for output in job.tool.outputs:
            extension = '.' + FormatsAccess.instance().get(output.type).extension

            # cmd
            output_file_name = output.name
            value = os.path.join(processed_data_dir, output_file_name + extension)
            cmd = cmd.replace("${" + output.name + "}", value)

            # output metadata
            processed_data = ProcessedData()
            processed_data.name = output.name
            processed_data.author = ConfigAccess.instance().get('user')['name']
            processed_data.date = format_date('now')
            processed_data.format = output.type

            processed_data.run_uri = run.md_uri
            processed_data.inputs = inputs_metadata

            processed_data.output = {
                'name': output.name,
                'label': output.description,
            }
            # save the metadata and create its md_uri and uri
            self.create_data(processed_dataset, run, processed_data)

        # 8- exec
        cmd = self._replace_env_variables(job.tool, cmd)
        cmd = cmd.replace('/', os.sep)
        job_id = self.new_job()
        self.notify(f'Start job{job_id}')
        self.runner_service.set_up(job.tool, job_id)
        self.runner_service.exec(job.tool, shlex.split(cmd), job_id)
        self.runner_service.tear_down(job.tool, job_id)
        self.notify_progress(100, 'done', job_id)
        self.notify(f'Finished job{job_id}')

    def run_pipeline(self, experiment: Experiment, pipeline: Pipeline):
        print('Start Pipeline')
        all_step_ran = False
        while not all_step_ran:
            loop_check = 0
            for step in pipeline.steps:
                if not step.already_ran:
                    job = Job()
                    job.set_experiment(experiment)
                    job.set_tool(self.get_tool(step.tool))
                    missing_inputs = False 
                    for input in step.inputs:
                        # Check that the input exists
                        if not self.is_dataset(experiment, input.dataset):
                            missing_inputs = True    
                        # continue if the inputs does not exists
                        job.set_input(name=input.name, dataset=input.dataset, 
                                      query=input.query, 
                                      origin_output_name=input.origin_output_name)
                    if not missing_inputs:                  
                        # set each parameters
                        for parameter in step.parameters:
                            print('job set param:', parameter.name, "=", parameter.value)
                            job.set_param(parameter.name, parameter.value)
                        # choose a name for the output dataset
                        job.set_output_dataset_name(step.output_dataset_name)
                        self.run(job) 
                        step.already_ran = True   
                else:
                    loop_check += 1
            if loop_check == len(pipeline.steps):
                all_step_ran = True 
        print('Start Pipeline')  
     
