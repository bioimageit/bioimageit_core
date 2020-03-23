import unittest
import os
import os.path
import filecmp
import shutil

from bioimagepy.experiment import Experiment
from tests.metadata import create_experiment
 
class TestLocalData(unittest.TestCase):
    def setUp(self):
        self.ref_experiment_file = 'tests/test_metadata_local/experiment.md.json'
        self.tst_experiment_file = 'tests/test_metadata_local/experiment_tst.md.json'
        self.tst_experiment_dir = 'tests/test_metadata_local/'

    def tearDown(self):
        if os.path.isfile(self.tst_experiment_file):
            os.remove(self.tst_experiment_file)
        path = os.path.join(self.tst_experiment_dir, 'myexperiment')
        if os.path.isdir(path):
            shutil.rmtree(path) 

    def test_read_experiment(self):
        read_experiment = Experiment(self.ref_experiment_file) 
        ref_experiment_container = create_experiment()
        self.assertEqual(read_experiment.metadata.serialize(), ref_experiment_container.serialize()) 

    def test_write_experiment(self):
        experiment = Experiment(self.tst_experiment_file)
        experiment.metadata = create_experiment()
        experiment.write()
        self.assertTrue(filecmp.cmp(self.tst_experiment_file, self.ref_experiment_file, shallow=False))

    def test_create_experiment(self):
        experiment = Experiment()
        metadata = create_experiment()
        experiment.create(metadata.name, metadata.author, metadata.date, self.tst_experiment_dir)  
        t1 = os.path.isdir( os.path.join(self.tst_experiment_dir, 'myexperiment') )
        t2 = os.path.isfile( os.path.join(self.tst_experiment_dir, 'myexperiment', 'experiment.md.json') )
        t3 = os.path.isdir( os.path.join(self.tst_experiment_dir, 'myexperiment', 'data') )
        t4 = os.path.isfile( os.path.join(self.tst_experiment_dir, 'myexperiment', 'data', 'rawdataset.md.json') )
        self.assertTrue(t1*t2*t3*t4)  