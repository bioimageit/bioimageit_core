
from bioimagepy.metadata.containers import (METADATA_TYPE_RAW, METADATA_TYPE_PROCESSED, 
                                            RawDataContainer, ProcessedDataContainer,
                                            DataSetContainer) 

def create_raw_data() -> RawDataContainer:
    rawDataContainer2 = RawDataContainer()
    rawDataContainer2.name = 'population1_001.tif'
    rawDataContainer2.author = 'Sylvain Prigent'
    rawDataContainer2.date = '2019-03-17'
    rawDataContainer2.uri = 'tests/test_metadata_local/data/population1_001.tif'
    rawDataContainer2.format = 'tif'
    rawDataContainer2.type = METADATA_TYPE_RAW()
    rawDataContainer2.tags['Population'] = 'population1'
    rawDataContainer2.tags['number'] = '001'
    return rawDataContainer2

def create_processed_data() -> ProcessedDataContainer:
    processedDataContainer2 = ProcessedDataContainer()
    processedDataContainer2.name = 'population1_001_o'
    processedDataContainer2.author = 'Sylvain Prigent'
    processedDataContainer2.date = '2020-03-04'
    processedDataContainer2.uri = 'tests/test_metadata_local/process1/population1_001_o.tif'
    processedDataContainer2.format = 'tif'
    processedDataContainer2.type = METADATA_TYPE_PROCESSED()
    processedDataContainer2.run_uri = "tests/test_metadata_local/process1/run.md.json"
    processedDataContainer2.add_input('i', 'tests/test_metadata_local/data/population1_001.md.json', METADATA_TYPE_RAW())
    processedDataContainer2.set_output('o', 'Denoised image')
    return processedDataContainer2

def create_dataset() -> DataSetContainer:   
    container = DataSetContainer()
    container.name = 'data'
    container.uris.append('tests/test_metadata_local/data/population1_001.md.json')
    container.uris.append('tests/test_metadata_local/data/population1_002.md.json')
    container.uris.append('tests/test_metadata_local/data/population1_003.md.json')
    return container