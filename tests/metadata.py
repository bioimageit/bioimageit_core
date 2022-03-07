import os
from bioimageit_core.containers.data_containers import (METADATA_TYPE_RAW,
                                                        METADATA_TYPE_PROCESSED,
                                                        Container,
                                                        RawData,
                                                        ProcessedData,
                                                        Dataset,
                                                        DatasetInfo,
                                                        Experiment)


def create_raw_data() -> RawData:
    raw_data_container2 = RawData()
    raw_data_container2.uuid = 'fake_uuid'
    raw_data_container2.name = 'population1_001.tif'
    raw_data_container2.author = 'Sylvain Prigent'
    raw_data_container2.date = '2019-03-17'
    raw_data_container2.uri = os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'data', 'population1_001.tif'))
    raw_data_container2.format = 'tif'
    raw_data_container2.type = METADATA_TYPE_RAW
    raw_data_container2.key_value_pairs['Population'] = 'population1'
    raw_data_container2.key_value_pairs['number'] = '001'
    return raw_data_container2


def create_processed_data() -> ProcessedData:
    processed_data_container2 = ProcessedData()
    processed_data_container2.uuid = 'fake_uuid'
    processed_data_container2.name = 'population1_001_o'
    processed_data_container2.author = 'Sylvain Prigent'
    processed_data_container2.date = '2020-03-04'
    processed_data_container2.uri = os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'process1', 'population1_001_o.tif'))
    processed_data_container2.format = 'tif'
    processed_data_container2.type = METADATA_TYPE_PROCESSED
    processed_data_container2.run = Container(os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'process1', 'run.md.json')),
        "fake_uuid")
    processed_data_container2.add_input_('i', os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'data', 'population1_001.md.json')),
                                        "fake_uuid",
                                        METADATA_TYPE_RAW)
    processed_data_container2.set_output('o', 'Denoised image')
    return processed_data_container2


def create_dataset() -> Dataset:
    container = Dataset()
    container.uuid = "fake_uuid"
    container.name = 'data'

    d1_url = os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'data', 'population1_001.md.json'))
    container.uris.append(Container(d1_url, 'fake_uuid'))

    d2_url = os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'data', 'population1_002.md.json'))
    container.uris.append(Container(d2_url, 'fake_uuid'))

    d3_url = os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'data', 'population1_003.md.json'))
    container.uris.append(Container(d3_url, 'fake_uuid'))
    return container


def create_experiment() -> Experiment:
    container = Experiment()
    container.uuid = "fake_uuid"
    container.name = 'myexperiment'
    container.author = 'Sylvain Prigent'
    container.date = '2020-03-04'

    raw_url = os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'data', 'rawdataset.md.json'))
    container.raw_dataset = DatasetInfo('data', raw_url, 'fake_uuid')

    p1_url = os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'process1', 'processeddataset.md.json'))
    container.processed_datasets.append(
        DatasetInfo('process1', p1_url, 'fake_uuid'))

    p2_url = os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'process2', 'processeddataset.md.json'))
    container.processed_datasets.append(
        DatasetInfo("process2", p2_url, 'fake_uuid'))

    container.keys.append('Population')
    container.keys.append('number')
    return container
