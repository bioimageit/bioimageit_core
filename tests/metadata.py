
from bioimagepy.metadata.containers import METADATA_TYPE_RAW, METADATA_TYPE_PROCESSED, RawDataContainer, ProcessedDataContainer

def create_raw_data() -> RawDataContainer:
    rawDataContainer2 = RawDataContainer()
    rawDataContainer2.name = 'celegans1'
    rawDataContainer2.author = 'Sylvain Prigent'
    rawDataContainer2.date = '2019-02-12'
    rawDataContainer2.uri = 'tests/test_metadata_local/celegans1.tif'
    rawDataContainer2.format = 'tif'
    rawDataContainer2.type = METADATA_TYPE_RAW()
    rawDataContainer2.tags['staining'] = 'blue'
    rawDataContainer2.tags['test'] = 'c2'
    rawDataContainer2.tags['wildtype/mutant'] = 'm'
    return rawDataContainer2

def create_processed_data() -> ProcessedDataContainer:
    processedDataContainer2 = ProcessedDataContainer()
    processedDataContainer2.name = 'celegans1_o'
    processedDataContainer2.author = 'Sylvain Prigent'
    processedDataContainer2.date = '2020-03-04'
    processedDataContainer2.uri = 'tests/test_metadata_local/celegans1_o.tif'
    processedDataContainer2.format = 'tif'
    processedDataContainer2.type = METADATA_TYPE_PROCESSED()
    processedDataContainer2.run_uri = "tests/test_metadata_local/run.md.json"
    processedDataContainer2.add_input('i', 'tests/test_metadata_local/rawdata.md.json', METADATA_TYPE_RAW())
    processedDataContainer2.set_output('o', 'Denoised image')
    return processedDataContainer2