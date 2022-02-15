"""Serialize the containers

Methods
-------
serialize_data
serialize_raw_data
serialize_processed_data
serialize_dataset
serialize_experiment
serialize_run

"""

from .data_containers import RawData, ProcessedData, Dataset, Run, Experiment


def serialize_data(data):
    """Serialize a data
    Parameters
    ----------
    data: Data
        Container of data metadata
    Returns
    -------
    str containing the serialized container
    """

    content = 'name = ' + data.name + '\n'
    content += 'author = ' + data.author + '\n'
    content += 'date = ' + data.date + '\n'
    content += 'format = ' + data.format + '\n'
    content += 'uri = ' + data.uri + '\n'
    return content


def serialize_raw_data(raw_data):
    """Serialize a raw data
    Parameters
    ----------
    raw_data: RawData
        Container of raw data metadata
    Returns
    -------
    str containing the serialized container
    """

    content = 'RawData:\n'
    content += serialize_data(raw_data)
    content += 'tags = {'
    for tag in raw_data.tags:
        content += raw_data.tags[tag] + ':' + raw_data.tags[tag] + ','
    content = content[:-1] + '}'
    return content


def serialize_processed_data(processed_data):
    """Serialize a processed_data

    Parameters
    ----------
    processed_data: ProcessedData
        Container of processed data metadata
    Returns
    -------
    str containing the serialized container

    """
    content = 'ProcessedData:\n'
    content += serialize_data(processed_data)
    content += 'run = \n'
    content += '\t{\n'
    content += '\t\tuuid: ' + processed_data.run.uuid + ',\n'
    content += '\t\turl: ' + processed_data.run.md_uri + ',\n'
    content += '\t}\n'
    content += 'inputs = [ \n'
    for input_ in processed_data.inputs:
        content += 'name:' + input_.name + ', uri:' + input_.uri + '\n'
    content += (
            'output={name:'
            + processed_data.output['name']
            + ', label:'
            + processed_data.output['label']
            + '}'
    )
    return content


def serialize_dataset(dataset):
    """Serialize a dataset
    Parameters
    ----------
    dataset: Dataset
        Container of dataset metadata
    Returns
    -------
    str containing the serialized container
    """

    content = 'Dataset:\n'
    content += 'name = ' + dataset.name
    content += 'uris = [\n'
    for uri in dataset.uris:
        content += '\t{\n'
        content += '\t\tuuid: ' + uri.uuid + ',\n'
        content += '\t\turl: ' + uri.md_uri + ',\n'
        content += '\t}\n'
    content += ']\n'
    return content


def serialize_experiment(experiment):
    """Serialize an experiment
    Parameters
    ----------
    experiment: Experiment
        Container of experiment metadata
    Returns
    -------
    str containing the serialized container
    """

    content = 'Experiment:\n'
    content += 'uuid = ' + experiment.uuid + '\n'
    content += 'name = ' + experiment.name + '\n'
    content += 'author = ' + experiment.author + '\n'
    content += 'date = ' + experiment.date + '\n'
    content += 'raw_dataset = ' + '\n'
    content += '\t{\n'
    content += '\t\tname: ' + experiment.raw_dataset.name + ',\n'
    content += '\t\tuuid: ' + experiment.raw_dataset.uuid + ',\n'
    content += '\t\turl: ' + experiment.raw_dataset.url + ',\n'
    content += '\t}\n'
    content += 'processed_datasets = [ \n'
    for dataset in experiment.processed_datasets:
        content += '\t{\n'
        content += '\t\tname: ' + dataset.name + ',\n'
        content += '\t\tuuid: ' + dataset.uuid + ',\n'
        content += '\t\turl: ' + dataset.url + ',\n'
        content += '\t}\n'
    content += '] \n'
    content += 'tags = [ \n'
    for tag in experiment.tag_keys:
        content += '\t' + tag + '\n'
    content += ']'
    return content


def serialize_run(run):
    """Serialize a run
    Parameters
    ----------
    run: Run
        Container of run metadata
    Returns
    -------
    str containing the serialized container
    """

    content = 'Experiment:\n'
    content += '{\n\t"process":{\n'
    content += '\t\t"name": "' + run.process_name + '",\n'
    content += '\t\t"uri": "' + run.process_uri + '"\n'
    content += '\t}\n\t"processed_dataset": \n'
    content += '\t\t{\n'
    content += '\t\t\t"uuid": "' + run.processed_dataset.uuid + '",\n'
    content += '\t\t\t"url": "' + run.processed_dataset.md_uri + '"\n'
    content += '\t\t},\n'
    content += '\t"parameters": [\n '
    for param in run.parameters:
        content += '\t\t{\n'
        content += '\t\t\t"name": "' + param.name + '",\n'
        content += '\t\t\t"value": "' + param.value + '"\n'
        content += '\t\t},\n'
    content = content[:-3] + '\n'
    content += '\t]\n'
    content += '\t"inputs": [\n '
    for input_ in run.inputs:
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
