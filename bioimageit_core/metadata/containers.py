# -*- coding: utf-8 -*-
"""BioImagePy metadata containers.

This module contains containers for metadata Data, Dataset,
Experiment 

Classes
------- 
DataContainer
RawDataContainer
ProcessedDataContainer
DataSetContainer
ExperimentContainer

"""


def METADATA_TYPE_RAW():
    """Type for matadata for raw data"""
    return "raw"


def METADATA_TYPE_PROCESSED():
    """Type for matadata for processed data"""
    return "processed"


class DataContainer:
    """Metadata container for generic data

    Attributes
    ----------
    name
        Name of the data
    author
        Author of the data
    date
        Date when the data is created
    format
        Data format (txt, csv, tif, ...)
    uri
        URI of the data as stored in the database

    """

    def __init__(self):
        self.name = ''
        self.author = ''
        self.date = ''
        self.format = ''
        self.uri = ''

    def serialize(self):
        content = 'name = ' + self.name + '\n'
        content += 'author = ' + self.author + '\n'
        content += 'date = ' + self.date + '\n'
        content += 'format = ' + self.format + '\n'
        content += 'uri = ' + self.uri + '\n'
        return content


class RawDataContainer(DataContainer):
    """Metadata container for raw data

    Attributes
    ----------
    tags
        Dictionary containing the tags (key=value)

    """

    def __init__(self):
        DataContainer.__init__(self)
        self.tags = dict()

    def serialize(self):
        content = 'RawData:\n'
        content += DataContainer.serialize(self)
        content += 'tags = {'
        for tag in self.tags:
            content += self.tags[tag] + ':' + self.tags[tag] + ','
        content = content[:-1] + '}'
        return content


class ProcessedDataInputContainer:
    """Container for processed data origin input

    Attributes
    ----------
    name
        Name of the input (the unique name in the process)
    uri
        The uri of the input metadata
    """

    def __init__(self, name: str = '', uri: str = '',
                 type_: str = METADATA_TYPE_RAW()):
        self.name = name
        self.uri = uri
        self.type = type_


class ProcessedDataContainer(DataContainer):
    """Metadata container for processed data

    Attributes
    ----------
    run_uri
        URI of the Run metadata file
    inputs
        Information about the inputs that generated
        this processed data. It is a list of ProcessedDataInputContainer
    output
        Information about how the output is referenced
        in the process that generates this processed data
        ex: {"name": "o", "label": "Processed image"}

    """

    def __init__(self):
        DataContainer.__init__(self)
        self.run_uri = ''
        self.inputs = list()
        self.output = dict()

    def add_input(self, name: str, uri: str, type_: str):
        self.inputs.append(ProcessedDataInputContainer(name, uri, type_))

    def set_output(self, name: str, label: str):
        self.output = {'name': name, 'label': label}

    def serialize(self):
        content = 'ProcessedData:\n'
        content += DataContainer.serialize(self)
        content += 'run_uri = ' + self.run_uri + '\n'
        content += 'inputs = [ \n'
        for input_ in self.inputs:
            content += 'name:' + input_.name + ', uri:' + input_.uri + '\n'
        content += (
            'output={name:'
            + self.output['name']
            + ', label:'
            + self.output['label']
            + '}'
        )
        return content


class DataSetContainer:
    def __init__(self):
        self.name = ''
        self.uris = list()

    def serialize(self):
        content = 'Dataset:\n'
        content += 'name = ' + self.name
        content += 'uris = \n'
        for uri in self.uris:
            content += '\t' + uri
        content += '\n'
        return content


class ExperimentContainer:
    def __init__(self):
        self.name = ''
        self.author = ''
        self.date = ''
        self.rawdataset = ''
        self.processeddatasets = []
        self.tags = []

    def serialize(self):
        content = 'Experiment:\n'
        content += 'name = ' + self.name + '\n'
        content += 'author = ' + self.author + '\n'
        content += 'date = ' + self.date + '\n'
        content += 'rawdataset = ' + self.rawdataset + '\n'
        content += 'processeddatasets = [ \n'
        for dataset in self.processeddatasets:
            content += '\t' + dataset + '\n'
        content += '] \n'
        content += 'tags = [ \n'
        for tag in self.tags:
            content += '\t' + tag + '\n'
        content += ']'
        return content

    def count_processed_dataset(self):
        return len(self.processeddatasets)

    def count_tags(self):
        return len(self.rawdataset)


class SearchContainer:
    """Container for data queries on tag

    Parameters
    ----------
    data
        Data are stored in dict as
            data['name] = 'file.tif'
            data['uri] = '/url/of/the/metadata/file.md.json'
            data['tags] = {'tag1'='value1', 'tag2'='value2'}

    """

    def __init__(self):
        self.data = dict()
        self.data['name'] = ''
        self.data['uri'] = ''
        self.data['tags'] = {}

    def uri(self):
        """Returns the data metadata file uri"""
        if 'uri' in self.data:
            return self.data['uri']

    def set_uri(self, uri: str):
        """Set the data metadata file uri"""
        self.data['uri'] = uri

    def set_name(self, name: str):
        self.data['name'] = name

    def name(self):
        return self.data['name']

    def is_tag(self, key: str):
        """Check if a tag exists

        Returns
        -------
        True if the tag exists, False otherwise

        """
        if key in self.data['tags']:
            return True
        return False

    def tag(self, key: str):
        """Get a tag value

        Parameters
        ----------
        key
            Tag key

        Returns
        -------
        value
            Value of the tag
        """
        if key in self.data['tags']:
            return self.data['tags'][key]
        return ''


class RunParameterContainer:
    def __init__(self, name: str = '', value: str = ''):
        self.name = name
        self.value = value


class RunInputContainer:
    def __init__(
        self,
        name: str = '',
        dataset: str = '',
        query: str = '',
        origin_output_name: str = '',
    ):
        self.name = name
        self.dataset = dataset
        self.query = query
        self.origin_output_name = origin_output_name


class RunContainer:
    def __init__(self):
        self.process_name = ''
        self.process_uri = ''
        self.processeddataset = ''
        self.parameters = []  # list of RunParameterContainer
        self.inputs = []  # list of RunInputContainer

    def serialize(self):
        content = 'Experiment:\n'
        content += '{\n\t"process":{\n'
        content += '\t\t"name": "' + self.process_name + '",\n'
        content += '\t\t"uri": "' + self.process_uri + '"\n'
        content += '\t}\n\t"processeddataset": "' + self.processeddataset + \
                   '",\n'
        content += '\t"parameters": [\n '
        for param in self.parameters:
            content += '\t\t{\n'
            content += '\t\t\t"name": "' + param.name + '",\n'
            content += '\t\t\t"value": "' + param.value + '"\n'
            content += '\t\t},\n'
        content = content[:-3] + '\n'
        content += '\t]\n'
        content += '\t"inputs": [\n '
        for input_ in self.inputs:
            content += '\t\t{\n'
            content += '\t\t\t"name": "' + input_.name + '",\n'
            content += '\t\t\t"dataset": "' + input_.dataset + '",\n'
            content += '\t\t\t"query": "' + input_.query + '",\n'
            content += (
                '\t\t\t"origin_output_name": "' + input_.origin_output_name +
                '"\n'
            )
            content += '\t\t},\n'
        content = content[:-3] + '\n'
        content += '\t]\n'
        content += '}'
        return content
