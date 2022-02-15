import unittest
import os
import os.path
import filecmp

from bioimageit_core.core.run import Run
from tests.test_run_local import create_run_metadata


class TestLocalRun(unittest.TestCase):
    def setUp(self):
        self.ref_run_file = os.path.join('tests', 'test_metadata_local', 'process1', 'run.md.json')
        self.tst_run_file = os.path.join('tests', 'test_metadata_local', 'process1', 'run_tst.md.json')

    def tearDown(self):
        if os.path.isfile(self.tst_run_file): 
            os.remove(self.tst_run_file)

    def test_read_run(self):
        run_read = Run(self.ref_run_file) 
        run_ref_metadata = create_run_metadata()
        self.assertEqual(run_read.metadata.serialize(),
                         run_ref_metadata.serialize())

    def test_write_run(self):
        run = Run(self.tst_run_file) 
        run.metadata = create_run_metadata()
        run.write()
        self.assertTrue(filecmp.cmp(self.tst_run_file, self.ref_run_file,
                                    shallow=False))
