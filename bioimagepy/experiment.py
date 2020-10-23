# -*- coding: utf-8 -*-
"""experiment module.

This module contains the Experiment class that allows to read/write and query
an experiment metadata.

Example
-------
    Here is an example of how to create an experiment and add data to it:

        >>> from bioimagepy.experiment import Experiment
        >>> myexperiment = Experiment()
        >>> myexperiment.create('myexperiment', 'Sylvain Prigent', './')
        >>> myexperiment.import_data(data_path='data_uri', name='mydata', author='Sylvain Prigent', format='tif, date = 'now', tags={}, copy = True))
        >>> myexperiment.import_dir(dir_uri='./my/local/dir/', filter='\.tif$', author='Sylvain Prigent', format='tif', date='now', copy_data=True)
        >>> myexperiment.tag_from_name(tag='population', ['population1', 'population2'])
        >>> myexperiment.tag_using_seperator(tag='ID', separator='_', value_position=1)
        >>> myexperiment.display()

Classes
-------
Experiment

"""

import os
import re
import datetime

from prettytable import PrettyTable

from bioimagepy.config import ConfigAccess
from bioimagepy.core.utils import Observable, format_date
from bioimagepy.data import RawData, ProcessedData
from bioimagepy.dataset import RawDataSet, ProcessedDataSet
from bioimagepy.metadata.factory import metadataServices
from bioimagepy.metadata.exceptions import MetadataQueryError
from bioimagepy.metadata.containers import RawDataContainer, ExperimentContainer

class Experiment(Observable):
    """Allows to interact with the matedata of an experiment

    Parameters
    ----------
    md_uri
        URI of the experiment in the database

    """
    def __init__(self, md_uri=''):
        Observable.__init__(self)
        self.md_uri = md_uri
        self.metadata = None
        config = ConfigAccess.instance().config['metadata']
        self.service = metadataServices.get(config["service"], **config)
        self.read()

    def read(self):
        """Read the metadata from database

        The data base connection is managed by the configuration
        object

        """
        self.metadata = self.service.read_experiment(self.md_uri)

    def write(self):
        """Write the metadata to database

        The data base connection is managed by the configuration
        object

        """
        self.service.write_experiment(self.metadata, self.md_uri)

    def create(self, name: str, author: str, date: str = 'now', uri:str = ''):
        """Create a new experiment

        The create method initialize a new experiment with
        the main metadata architecture

        Parameters
        ----------
        name
            Name of the experiment
        author
            Name of the person who created the experiment
        uri
            URI of the experiment. For local it is the directory
            where the experiment will be saved. For Omero, it is the
            user workspace

        """
        self.metadata = ExperimentContainer()
        self.metadata.name = name
        self.metadata.author = author
        self.metadata.date = format_date(date)
        self.md_uri = self.service.create_experiment(self.metadata, uri)

    def create_processed_dataset(self, name:str) -> ProcessedDataSet:
        """Create an empty processed dataset

        Parameters
        ----------
        name
            Name of the dataset
        run
            Object containing the Run informations

        """
        container, md_uri = self.service.create_processed_dataset(name, self.md_uri)
        dataset = ProcessedDataSet()
        dataset.metadata = container
        dataset.md_uri = md_uri
        return dataset

    def import_data(self, data_path:str, name:str, author:str, format:str, date:str = 'now', tags:dict = {}, copy:bool = True):
        """import one data to the experiment

        The data is imported to the rawdataset

        Parameters
        ----------
        data_path
            Path of the accessible data on your local computer
        name
            Name of the data
        author
            Person who created the data
        format:
            Format of the data (ex: tif)
        date
            Date when the data where created
        tags
            Dictonnary {key:value, key:value} of tags
        copy
            True to copy the data to the Experiment database
            False otherwhise

        Returns
        -------
        class RawData containing the metadata

        """
        metadata = RawDataContainer()
        metadata.name = name
        metadata.author = author
        metadata.format = format
        metadata.date = format_date(date)
        metadata.tags = tags
        data_uri = self.service.import_data(data_path, self.metadata.rawdataset, metadata, copy)
        return RawData(data_uri)

    def import_dir(self, dir_uri:str, filter:str, author:str, format:str, date:str, copy_data:bool):
        """Import data from a directory to the experiment

        This method import with or whitout copy data contained
        in a local folder into an experiment. Imported data are
        considered as RawData for the experiment

        Parameters
        ----------
        dir_uri
            URI of the directory containing the data to be imported
        filter
            Regular expression to filter which files in the folder
            to import
        author
            Name of the person who created the data
        format
            Format of the image (ex: tif)
        date
            Date when the data where created
        copy_data
            True to copy the data to the experiment, false otherwise. If the
            data are not copied, an absolute link to dir_uri is kept in the
            experiment metadata. The original data directory must then not be
            changed for the experiment to find the data.

        """
        files = os.listdir(dir_uri)
        count = 0
        for file in files:
            count += 1
            r1 = re.compile(filter) # re.compile(r'\.tif$')
            if r1.search(file):
                self.notify_observers(int(100*count/len(files)), file)
                data_url = os.path.join(dir_uri, file)
                self.import_data(data_url, file, author, format, date, {}, copy_data )


    def display(self, dataset:str='data'):
        """Display a dataset content as a table in the console

        Parameters
        ----------
        dataset
            Name of the dataset to display

        """
        """Display inherited from BiObject"""

        print("--------------------")
        print("Experiment: ")
        print("\tName: ", self.metadata.name)
        print("\tAuthor: ", self.metadata.author)
        print("\tCreated: ", self.metadata.date)
        print("\tTags: ")
        for tag in self.metadata.tags:
            print('\t\t-', tag)
        print("\tDataSet: ", dataset)
        tags = self.metadata.tags
        t = PrettyTable(['Name'] + tags + ['Author', 'Created date'])
        if dataset == 'data':
            rawdataset = self.get_dataset(dataset)
            for i in range(rawdataset.size()):
                rawdata = rawdataset.get(i)
                tags_values = []
                for key in tags:
                    tags_values.append(rawdata.tag(key))
                t.add_row( [ rawdata.metadata.name ] + tags_values + [ rawdata.metadata.author, rawdata.metadata.date ] )
        else:
            # TODO implement display processed dataset
            print('Display processed dataset not yet implemented')
        print(t)

    def set_tag(self, tag: str, add_to_data: bool = True):
        """Add a tag key to the experiment

        It add the tag key (if not already exists) to the
        experiment metadata and also add a tag key to all
        the images

        Parameters
        ----------
        tag
            Tag key to be added
        add_to_data
            if True add an empty tag to all the data in
            the RawDataSet

        """
        # add the tag to the experiment
        if tag not in self.metadata.tags:
            self.metadata.tags.append(tag)
            self.write()
        if add_to_data:
            raw_dataset = RawDataSet(self.metadata.rawdataset)
            for i in range(raw_dataset.size):
                raw_data = raw_dataset.get(i)
                if tag not in raw_data.metadata.tags:
                    raw_data.set_tag(tag, '')


    def tag_from_name(self, tag: str, values: list):
        """Tag an experiment raw data using file name

        Parameters
        ----------
        tag
            The name (or key) of the tag to add to the data
        values
            List of possible values for the tag to find in the filename

        """
        self.set_tag(tag, False)
        _rawdataset = RawDataSet(self.metadata.rawdataset)
        for i in range(_rawdataset.size()):
            _rawdata = _rawdataset.get(i)
            for value in values:
                if value in _rawdata.metadata.name:
                    _rawdata.set_tag(tag, value)
                    break

    def tag_using_seperator(self, tag: str, separator: str, value_position: int):
        """Tag an experiment raw data using file name and separator

        Parameters
        ----------
        tag
            The name (or key) of the tag to add to the data
        separator
            The character used as a separator in the filename (ex: _)
        value_position
            Position of the value to extract with respect to the separators

        """
        self.set_tag(tag, False)
        _rawdataset = RawDataSet(self.metadata.rawdataset)
        for i in range(_rawdataset.size()):
            _rawdata = _rawdataset.get(i)
            basename = os.path.splitext(os.path.basename(_rawdata.metadata.uri))[0]
            splited_name = basename.split(separator)
            value = ''
            if len(splited_name) > value_position:
                value = splited_name[value_position]
            _rawdata.set_tag(tag, value)

    def get_processed_datasets_size(self):
        """Get the number of processed datasets

        Returns
        -------
        The number of processed datasets

        """
        return len(self.metadata.processeddatasets)

    def get_processed_dataset_at(self, idx: int):
        """Get a processed dataset

        Parameters
        ----------
        idx
            Index of the processed dataset in the processed dataset list

        Returns
        -------
        ProcessedDataSet at idx
        """
        return ProcessedDataSet(self.metadata.processeddatasets[idx])

    def get_dataset(self, name:str):
        """Get the metadata of a dataset

        Returns a RawDataset or a ProcessedDataSet

        Parameters
        ----------
        name
            Name of the dataset

        """
        if name == 'data':
            return RawDataSet(self.metadata.rawdataset)
        else:
            for dataset_name in self.metadata.processeddatasets:
                pdataset = ProcessedDataSet(dataset_name)
                if pdataset.metadata.name == name:
                    return pdataset
        return None

    def get_data(self, dataset_name: str, query: str, origin_output_name: str = '') -> list:
        """query a specific dataset of an experiment

        In this verion only AND queries are supported (ex: tag1=value1 AND tag2=value2)
        and performed on the data set named dataset

        Parameters
        ----------
        dataset_name
            Name of the dataset to query
        query
            String query with the key=value format.
        origin_output_name
            Name of the ouput origin (ex: -o) in the case of ProcessedDataset search

        Returns
        -------
        list
            List of selected data (md.json files urls are returned)

        """
        # search the dataset
        raw_dataset = RawDataSet(self.metadata.rawdataset)
        if raw_dataset.metadata.name == dataset_name:
            return raw_dataset.get_data(query)
        else:
            for i in range(len(self.metadata.processeddatasets)):
                processeddataset = ProcessedDataSet(self.metadata.processeddatasets[i])
                if processeddataset.metadata.name == dataset_name:
                    return processeddataset.get_data(query, origin_output_name)

        raise MetadataQueryError('Query dataset ', dataset_name, ' not found')


