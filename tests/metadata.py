import os
from bioimageit_core.metadata.containers import (METADATA_TYPE_RAW,
                                                 METADATA_TYPE_PROCESSED,
                                                 RawDataContainer,
                                                 ProcessedDataContainer,
                                                 DataSetContainer,
                                                 ExperimentContainer)


def create_raw_data() -> RawDataContainer:
    raw_data_container2 = RawDataContainer()
    raw_data_container2.name = 'population1_001.tif'
    raw_data_container2.author = 'Sylvain Prigent'
    raw_data_container2.date = '2019-03-17'
    raw_data_container2.uri = os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'data', 'population1_001.tif'))
    raw_data_container2.format = 'tif'
    raw_data_container2.type = METADATA_TYPE_RAW()
    raw_data_container2.tags['Population'] = 'population1'
    raw_data_container2.tags['number'] = '001'
    return raw_data_container2


def create_processed_data() -> ProcessedDataContainer:
    processed_data_container2 = ProcessedDataContainer()
    processed_data_container2.name = 'population1_001_o'
    processed_data_container2.author = 'Sylvain Prigent'
    processed_data_container2.date = '2020-03-04'
    processed_data_container2.uri = os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'process1', 'population1_001_o.tif'))
    processed_data_container2.format = 'tif'
    processed_data_container2.type = METADATA_TYPE_PROCESSED()
    processed_data_container2.run_uri = os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'process1', 'run.md.json'))
    processed_data_container2.add_input('i', os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'data', 'population1_001.md.json')),
                                        METADATA_TYPE_RAW())
    processed_data_container2.set_output('o', 'Denoised image')
    return processed_data_container2


def create_dataset() -> DataSetContainer:   
    container = DataSetContainer()
    container.name = 'data'
    container.uris.append(os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'data', 'population1_001.md.json')))
    container.uris.append(os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'data', 'population1_002.md.json')))
    container.uris.append(os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'data', 'population1_003.md.json')))
    return container


def create_experiment() -> ExperimentContainer:
    container = ExperimentContainer()
    container.name = 'myexperiment'
    container.author = 'Sylvain Prigent'
    container.date = '2020-03-04'
    container.rawdataset = os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'data', 'rawdataset.md.json'))
    container.processeddatasets.append(os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'process1', 'processeddataset.md.json')))
    container.processeddatasets.append(os.path.abspath(os.path.join(
        'tests', 'test_metadata_local', 'process2', 'processeddataset.md.json')))
    container.tags.append('Population')
    container.tags.append('number')
    return container
