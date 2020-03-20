import unittest
import filecmp
import os.path

from bioimagepy.metadata.containers import METADATA_TYPE_RAW, METADATA_TYPE_PROCESSED, RawDataContainer, ProcessedDataContainer
from bioimagepy.metadata.local import LocalMetadataService, relative_path, absolute_path

from bioimagepy.data import RawData, ProcessedData
from tests.metadata import create_raw_data, create_processed_data, create_dataset


class TestMetadataLocalFunctions(unittest.TestCase):

    def test_relative_path1(self):
        reference_file = 'my/computer/experiment/data/rawdata.md.json'
        file = 'my/computer/experiment/data/rawdata.tif'
        relative_file = relative_path(file, reference_file)
        self.assertEqual(relative_file, 'rawdata.tif')

    def test_relative_path2(self):   
        reference_file = 'my/computer/experiment/svdeconv/processeddata.md.json'
        file = 'my/computer/experiment/data/raw.md.json'
        relative_file = relative_path(file, reference_file) 
        self.assertEqual(relative_file, '../data/raw.md.json')

    def test_absolute_path(self):   
        reference_file = 'my/computer/experiment/data/rawdata.md.json'
        file = 'rawdata.tif'
        abs_file = absolute_path(file, reference_file)  
        self.assertEqual(abs_file, 'my/computer/experiment/data/rawdata.tif')  


class TestLocalMetadataService(unittest.TestCase):

    def setUp(self):
        self.service = LocalMetadataService()
        self.ref_rawdata_file = 'tests/test_metadata_local/rawdata.md.json'
        self.tst_rawdata_file = 'tests/test_metadata_local/rawdata_tst.md.json'
        self.ref_processeddata_file = 'tests/test_metadata_local/processeddata.md.json'
        self.tst_processeddata_file = 'tests/test_metadata_local/processeddata_tst.md.json'
        self.ref_dataset_file = 'tests/test_metadata_local/dataset.md.json'
        self.tst_dataset_file = 'tests/test_metadata_local/dataset_tst.md.json'

    def tearDown(self):
        if os.path.isfile(self.tst_rawdata_file): 
            os.remove(self.tst_rawdata_file)
        if os.path.isfile(self.tst_processeddata_file): 
            os.remove(self.tst_processeddata_file)   
        if os.path.isfile(self.tst_dataset_file):
            os.remove(self.tst_dataset_file)     

    def test_read_rawdata(self):
        rawDataContainer1 = self.service.read_rawdata(self.ref_rawdata_file)
        rawDataContainer2 = create_raw_data()
        self.assertEqual(rawDataContainer1.serialize(), rawDataContainer2.serialize())

    def test_write_rawdata(self):
        rawDataContainer2 = create_raw_data()
        self.service.write_rawdata(rawDataContainer2, self.tst_rawdata_file)
        self.assertTrue(filecmp.cmp(self.tst_rawdata_file, self.ref_rawdata_file, shallow=False))

    def test_read_processeddata(self):
        processedDataContainer1 = self.service.read_processeddata(self.ref_processeddata_file)
        processedDataContainer2 = create_processed_data()
        self.assertEqual(processedDataContainer1.serialize(), processedDataContainer2.serialize())

    def test_write_processeddata(self):
        processedDataContainer2 = create_processed_data()
        self.service.write_processeddata(processedDataContainer2, self.tst_processeddata_file)
        self.assertTrue(filecmp.cmp(self.tst_processeddata_file, self.ref_processeddata_file, shallow=False))

    def test_read_rawdataset(self):
        reff_dataset = create_dataset()
        read_dataset = self.service.read_rawdataset(self.ref_dataset_file)
        self.assertEqual(reff_dataset.serialize(), read_dataset.serialize())
        return True 

    def test_write_rawdataset(self):
        container = create_dataset()
        self.service.write_rawdataset(container, self.tst_dataset_file) 
        self.assertTrue(filecmp.cmp(self.tst_dataset_file, self.ref_dataset_file, shallow=False))   

    def test_read_processeddataset(self):
        reff_dataset = create_dataset()
        read_dataset = self.service.read_processeddataset(self.ref_dataset_file)
        self.assertEqual(reff_dataset.serialize(), read_dataset.serialize())

    def test_write_processeddataset(self):
        container = create_dataset()
        self.service.write_processeddataset(container, self.tst_dataset_file) 
        self.assertTrue(filecmp.cmp(self.tst_dataset_file, self.ref_dataset_file, shallow=False))      

if __name__ == '__main__':
    unittest.main()    