import unittest
import os
import os.path
import filecmp
import shutil

from bioimageit_core.experiment import Experiment
from bioimageit_core.data import RawData
from tests.metadata import create_experiment


class TestLocalData(unittest.TestCase):
    def setUp(self):
        self.ref_experiment_file = \
            os.path.join('tests', 'test_metadata_local', 'experiment.md.json')
        self.tst_experiment_file = \
            os.path.join('tests', 'test_metadata_local', 'experiment_tst.md.json')
        self.tst_experiment_dir = os.path.join('tests', 'test_metadata_local') + os.sep

    def _create_experiment(self):
        experiment = Experiment()
        metadata = create_experiment()
        experiment.create(metadata.name, metadata.author, metadata.date,
                          self.tst_experiment_dir)
        return experiment  

    def tearDown(self):
        if os.path.isfile(self.tst_experiment_file):
            os.remove(self.tst_experiment_file)
        path = os.path.join(self.tst_experiment_dir, 'myexperiment')
        if os.path.isdir(path):
            shutil.rmtree(path) 

    def test_read_experiment(self):
        read_experiment = Experiment(self.ref_experiment_file) 
        ref_experiment_container = create_experiment()
        self.assertEqual(read_experiment.metadata.serialize(),
                         ref_experiment_container.serialize())

    def test_write_experiment(self):
        experiment = Experiment(self.tst_experiment_file)
        experiment.metadata = create_experiment()
        experiment.write()
        self.assertTrue(filecmp.cmp(self.tst_experiment_file,
                                    self.ref_experiment_file, shallow=False))

    def test_create_experiment(self):
        experiment = Experiment()
        metadata = create_experiment()
        experiment.create(metadata.name, metadata.author, metadata.date,
                          self.tst_experiment_dir)
        t1 = os.path.isdir(os.path.join(self.tst_experiment_dir,
                                        'myexperiment'))
        t2 = os.path.isfile(os.path.join(self.tst_experiment_dir,
                                         'myexperiment',
                                         'experiment.md.json'))
        t3 = os.path.isdir(os.path.join(self.tst_experiment_dir,
                                        'myexperiment',
                                        'data'))
        t4 = os.path.isfile(os.path.join(self.tst_experiment_dir,
                                         'myexperiment',
                                         'data',
                                         'rawdataset.md.json'))
        self.assertTrue(t1*t2*t3*t4)  

    def test_import_data(self):
        experiment = self._create_experiment()
        data = experiment.import_data(
            os.path.join('tests', 'test_images', 'data', 'population1_001.tif'),
            'population1_001.tif',
            'Sylvain Prigent',
            'tif',
            'now',
            {"Population": "p1"},
            True)
        t1 = os.path.isfile(os.path.join(self.tst_experiment_dir,
                                         'myexperiment',
                                         'data',
                                         'population1_001.md.json'))
        t2 = False
        if data.metadata.name == 'population1_001.tif':
            t2 = True
        t3 = os.path.isfile(os.path.join(self.tst_experiment_dir,
                                         'myexperiment',
                                         'data',
                                         'population1_001.tif'))
        t4 = False
        if data.metadata.tags['Population'] == 'p1':
            t4 = True
        self.assertTrue(t1*t2*t3*t4)

    def test_import_dir(self):
        experiment = self._create_experiment()
        experiment.import_dir(os.path.join('tests', 'test_images', 'data') + os.sep,
                              r'\.tif$',
                              'Sylvain Prigent',
                              'tif',
                              'now',
                              True)
        data_dir = os.path.join(self.tst_experiment_dir, 'myexperiment', 'data')
        data_files = next(os.walk(data_dir))[2]  # to count files in data dir
        # count the number of imported files
        t1 = False
        if len(data_files) == 81:  
            t1 = True  
        # count the number of lines in the rawdataset.md.json file    
        t2 = False
        fd = open(os.path.join(data_dir, 'rawdataset.md.json'))
        number_of_lines = len(fd.readlines())
        fd.close()
        if number_of_lines == 45:
            t2 = True   
        self.assertTrue(t1*t2)  

    def test_set_tag(self):
        experiment = self._create_experiment()
        experiment.set_tag('Population', False)
        exp2 = Experiment(os.path.join(self.tst_experiment_dir,
                                       'myexperiment',
                                       'experiment.md.json'))
        self.assertTrue('Population' in exp2.metadata.tags)

    def test_tag_from_name(self):
        experiment = self._create_experiment()
        experiment.import_dir(os.path.join('tests', 'test_images', 'data') + os.sep,
                              r'\.tif$',
                              'Sylvain Prigent',
                              'tif',
                              'now',
                              True)
        experiment.tag_from_name('Population', ['population1', 'population2'])
        # test if tag Population in the experiment metadata
        t1 = False
        if 'Population' in experiment.metadata.tags:
            t1 = True
        # test few images tags
        data1 = RawData(os.path.join(self.tst_experiment_dir,
                                     "myexperiment",
                                     'data',
                                     'population1_012.md.json'))
        t2 = False
        if 'Population' in data1.metadata.tags and \
                data1.metadata.tags['Population'] == 'population1':
            t2 = True
        data2 = RawData(os.path.join(self.tst_experiment_dir,
                                     "myexperiment",
                                     'data',
                                     'population2_011.md.json'))
        t3 = False
        if 'Population' in data2.metadata.tags and \
                data2.metadata.tags['Population'] == 'population2':
            t3 = True    
        self.assertTrue(t1*t2*t3)    

    def test_tag_using_seperator(self):
        experiment = self._create_experiment()
        experiment.import_dir(os.path.join('tests', 'test_images', 'data') + os.sep,
                              r'\.tif$', 'Sylvain Prigent', 'tif', 'now', True)
        experiment.tag_using_seperator('ID', '_', 1)
        # test if tag ID in the experiment metadata
        t1 = False
        if 'ID' in experiment.metadata.tags:
            t1 = True
        # test few images tags
        data1 = RawData(os.path.join(self.tst_experiment_dir,
                                     "myexperiment",
                                     'data',
                                     'population1_012.md.json'))
        t2 = False
        if 'ID' in data1.metadata.tags and data1.metadata.tags['ID'] == '012':
            t2 = True
        data2 = RawData(os.path.join(self.tst_experiment_dir,
                                     "myexperiment",
                                     'data',
                                     'population2_011.md.json'))
        t3 = False
        if 'ID' in data2.metadata.tags and data2.metadata.tags['ID'] == '011':
            t3 = True    
        self.assertTrue(t1*t2*t3)   

    def test_get_dataset1(self):
        # raw dataset
        experiment = Experiment(self.ref_experiment_file)
        raw_dataset = experiment.get_dataset('data')    
        self.assertEqual(raw_dataset.metadata.name, 'data') 

    def test_get_dataset2(self):
        # processed dataset
        experiment = Experiment(self.ref_experiment_file)
        raw_dataset = experiment.get_dataset('process1')    
        self.assertEqual(raw_dataset.metadata.name, 'process1')        

    def test_get_data1(self):
        experiment = self._create_experiment()
        experiment.import_dir(os.path.join('tests', 'test_images', 'data') + os.sep,
                              r'\.tif$',
                              'Sylvain Prigent',
                              'tif', 'now', True)
        experiment.tag_from_name('Population', ['population1', 'population2'])
        experiment.tag_using_seperator('ID', '_', 1)
        data_list = experiment.get_data('data', 'Population=population1')
        self.assertEqual(len(data_list), 20)

    def test_get_data2(self):
        experiment = self._create_experiment()
        experiment.import_dir(os.path.join('tests', 'test_images', 'data') + os.sep,
                              r'\.tif$',
                              'Sylvain Prigent',
                              'tif', 'now', True)
        experiment.tag_from_name('Population', ['population1', 'population2'])
        experiment.tag_using_seperator('ID', '_', 1)
        data_list = experiment.get_data('data',
                                        'Population=population2 AND ID<=2')
        self.assertEqual(len(data_list), 2)
