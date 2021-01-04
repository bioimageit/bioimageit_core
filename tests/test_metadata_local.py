import unittest
import filecmp
import os.path
import shutil

from bioimageit_core.metadata.service_local import (LocalMetadataService,
                                                    relative_path,
                                                    absolute_path,
                                                    simplify_path)
from tests.metadata import (create_raw_data, create_processed_data, 
                            create_dataset, create_experiment)


class TestMetadataLocalFunctions(unittest.TestCase):

    def test_simplify_path1(self):
        sep = os.sep
        file = sep+'my'+sep+'computer'+sep+'experiment'+sep+'svdeconv'+sep+'..'+sep+'data'+sep+'raw.md.json'
        simplified_file = simplify_path(file)    
        self.assertEqual(simplified_file,
                         sep+'my'+sep+'computer'+sep+'experiment'+sep+'data'+sep+'raw.md.json')

    def test_simplify_path2(self):
        sep = os.sep
        file = sep + 'my' + sep + 'computer' + sep + 'experiment' + sep + 'svdeconv' + sep + 'denoise' + sep + '..' + \
               sep + '..' + sep + 'data' + sep + 'raw.md.json'
        simplified_file = simplify_path(file)    
        self.assertEqual(simplified_file,
                         sep + 'my' + sep + 'computer' + sep + 'experiment' + sep + 'data' + sep + 'raw.md.json')
        
    def test_relative_path1(self):
        sep = os.sep
        reference_file = 'my' + sep + 'computer' + sep + 'experiment' + sep + 'data' + sep + 'rawdata.md.json'
        file = 'my' + sep + 'computer' + sep + 'experiment' + sep + 'data' + sep + 'rawdata.tif'
        relative_file = relative_path(file, reference_file)
        self.assertEqual(relative_file, 'rawdata.tif')

    def test_relative_path2(self):
        sep = os.sep
        reference_file = 'my' + sep + 'computer' + sep + 'experiment' + sep + 'svdeconv' + sep + 'processeddata.md.json'
        file = 'my' + sep + 'computer' + sep + 'experiment' + sep + 'data' + sep + 'raw.md.json'
        relative_file = relative_path(file, reference_file) 
        self.assertEqual(relative_file, '..' + sep + 'data' + sep + 'raw.md.json')

    def test_absolute_path(self):
        sep = os.sep
        reference_file = 'my' + sep + 'computer' + sep + 'experiment' + sep + 'data' + sep + 'rawdata.md.json'
        file = 'rawdata.tif'
        abs_file = absolute_path(file, reference_file)  
        self.assertEqual(abs_file, 'my' + sep + 'computer' + sep + 'experiment' + sep + 'data' + sep + 'rawdata.tif')


class TestLocalMetadataService(unittest.TestCase):

    def setUp(self):
        sep = os.sep
        self.service = LocalMetadataService()
        self.ref_rawdata_file = \
            'tests' + sep + 'test_metadata_local' + sep + 'data' + sep + 'population1_001.md.json'
        self.tst_rawdata_file = \
            'tests' + sep + 'test_metadata_local' + sep + 'data' + sep + 'population1_001_tst.md.json'
        self.ref_processeddata_file = \
            'tests' + sep + 'test_metadata_local' + sep + 'process1' + sep + 'population1_001_o.md.json'
        self.tst_processeddata_file = \
            'tests' + sep + 'test_metadata_local' + sep + 'process1' + sep + 'population1_001_o_tst.md.json'
        self.ref_processeddata2_file = \
            'tests' + sep + 'test_metadata_local' + sep + 'process1' + sep + 'population1_002_o.md.json'
        self.ref_dataset_file = \
            'tests' + sep + 'test_metadata_local' + sep + 'data' + sep + 'rawdataset.md.json'
        self.tst_dataset_file = \
            'tests' + sep + 'test_metadata_local' + sep + 'data' + sep + 'rawdataset_tst.md.json'
        self.ref_experiment_file = \
            'tests' + sep + 'test_metadata_local' + sep + 'experiment.md.json'
        self.tst_experiment_file = \
            'tests' + sep + 'test_metadata_local' + sep + 'experiment_tst.md.json'
        self.tst_experiment_dir = \
            'tests' + sep + 'test_metadata_local' + sep

    def tearDown(self):
        if os.path.isfile(self.tst_rawdata_file):
            os.remove(self.tst_rawdata_file)
        if os.path.isfile(self.tst_processeddata_file):
            os.remove(self.tst_processeddata_file)
        if os.path.isfile(self.tst_dataset_file):
            os.remove(self.tst_dataset_file)
        if os.path.isfile(self.tst_experiment_file):
            os.remove(self.tst_experiment_file)
        path = os.path.join(self.tst_experiment_dir, 'myexperiment')
        if os.path.isdir(path):
            shutil.rmtree(path)
        pass

    def test_read_rawdata(self):
        raw_data_container1 = self.service.read_rawdata(self.ref_rawdata_file)
        raw_data_container2 = create_raw_data()
        self.assertEqual(raw_data_container1.serialize(),
                         raw_data_container2.serialize())

    def test_write_rawdata(self):
        raw_data_container2 = create_raw_data()
        self.service.write_rawdata(raw_data_container2, self.tst_rawdata_file)
        self.assertTrue(filecmp.cmp(self.tst_rawdata_file,
                                    self.ref_rawdata_file,
                                    shallow=False))

    def test_read_processeddata(self):
        processed_data_container1 = self.service.read_processeddata(
            self.ref_processeddata_file)
        processed_data_container2 = create_processed_data()
        self.assertEqual(processed_data_container1.serialize(),
                         processed_data_container2.serialize())

    def test_write_processeddata(self):
        processed_data_container2 = create_processed_data()
        self.service.write_processeddata(processed_data_container2,
                                         self.tst_processeddata_file)
        self.assertTrue(filecmp.cmp(self.tst_processeddata_file,
                                    self.ref_processeddata_file,
                                    shallow=False))

    def test_read_rawdataset(self):
        reff_dataset = create_dataset()
        read_dataset = self.service.read_rawdataset(self.ref_dataset_file)
        self.assertEqual(reff_dataset.serialize(), read_dataset.serialize())
        return True 

    def test_write_rawdataset(self):
        container = create_dataset()
        self.service.write_rawdataset(container, self.tst_dataset_file) 
        self.assertTrue(filecmp.cmp(self.tst_dataset_file,
                                    self.ref_dataset_file,
                                    shallow=False))

    def test_read_processeddataset(self):
        reff_dataset = create_dataset()
        read_dataset = self.service.read_processeddataset(self.ref_dataset_file)
        self.assertEqual(reff_dataset.serialize(), read_dataset.serialize())

    def test_write_processeddataset(self):
        container = create_dataset()
        self.service.write_processeddataset(container, self.tst_dataset_file) 
        self.assertTrue(filecmp.cmp(self.tst_dataset_file,
                                    self.ref_dataset_file,
                                    shallow=False))

    def test_read_experiment(self):
        ref_container = create_experiment() 
        read_container = self.service.read_experiment(self.ref_experiment_file)
        self.assertEqual(ref_container.serialize(), read_container.serialize())

    def test_write_experiment(self):
        container = create_experiment()
        self.service.write_experiment(container, self.tst_experiment_file) 
        self.assertTrue(filecmp.cmp(self.tst_experiment_file,
                                    self.ref_experiment_file,
                                    shallow=False))

    def test_create_experiment(self):
        container = create_experiment()
        self.service.create_experiment(container, self.tst_experiment_dir)
        t1 = os.path.isdir(os.path.join(self.tst_experiment_dir,
                                        'myexperiment'))
        t2 = os.path.isfile(os.path.join(self.tst_experiment_dir,
                                         'myexperiment',
                                         'experiment.md.json'))
        t3 = os.path.isdir(os.path.join(self.tst_experiment_dir,
                                        'myexperiment', 'data'))
        t4 = os.path.isfile(os.path.join(self.tst_experiment_dir,
                                         'myexperiment', 'data',
                                         'rawdataset.md.json'))
        self.assertTrue(t1*t2*t3*t4)


if __name__ == '__main__':
    unittest.main()
