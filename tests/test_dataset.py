import unittest
import os
import os.path
import filecmp

from bioimagepy.dataset import RawDataSet, ProcessedDataSet
from tests.metadata import create_dataset
from bioimagepy.metadata.service_local import relative_path

class TestLocalDataSet(unittest.TestCase):
    def setUp(self):
        self.ref_dataset_file = 'tests/test_metadata_local/data/rawdataset.md.json'
        self.tst_dataset_file = 'tests/test_metadata_local/data/rawdataset_tst.md.json'

    def tearDown(self):
        if os.path.isfile(self.tst_dataset_file):
            os.remove(self.tst_dataset_file)  

    def test_read_rawdataset(self):
        raw_dataset_read = RawDataSet(self.ref_dataset_file) 
        raw_data_ref_metadata = create_dataset()
        self.assertEqual(raw_dataset_read.metadata.serialize(), raw_data_ref_metadata.serialize()) 

    def test_write_rawdataset(self):
        raw_data = RawDataSet(self.tst_dataset_file)
        raw_data.metadata = create_dataset()
        raw_data.write()
        self.assertTrue(filecmp.cmp(self.tst_dataset_file, self.ref_dataset_file, shallow=False))

    def test_read_processeddata(self):
        raw_dataset_read = ProcessedDataSet(self.ref_dataset_file) 
        raw_data_ref_metadata = create_dataset()
        self.assertEqual(raw_dataset_read.metadata.serialize(), raw_data_ref_metadata.serialize()) 

    def test_write_processeddata(self):
        raw_data = ProcessedDataSet(self.tst_dataset_file)
        raw_data.metadata = create_dataset()
        raw_data.write()
        self.assertTrue(filecmp.cmp(self.tst_dataset_file, self.ref_dataset_file, shallow=False))

