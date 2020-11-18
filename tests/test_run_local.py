import unittest
import os
import os.path
import filecmp

from bioimageit_core.metadata.service_local import LocalMetadataService
from bioimageit_core.metadata.containers import (RunContainer,
                                                 RunInputContainer,
                                                 RunParameterContainer)


def create_run_metadata():
    container = RunContainer()
    container.process_name = 'SPARTION 2D'
    container.process_uri = '../galaxytools/tools/svdeconv/svdeconv2d.xml'
    container.processeddataset = 'processeddataset.md.json'
    container.inputs.append(RunInputContainer('i', 'data', '', ''))
    container.parameters.append(RunParameterContainer("sigma", "3"))
    container.parameters.append(RunParameterContainer("weighting", "0.1"))
    container.parameters.append(RunParameterContainer("regularization", "2"))
    container.parameters.append(RunParameterContainer("method", "SV"))
    return container


class TestLocalRunService(unittest.TestCase):

    def setUp(self):
        self.service = LocalMetadataService()
        self.ref_run_file = 'tests/test_metadata_local/process1/run.md.json'
        self.tst_run_file = 'tests/test_metadata_local/process1/run_tst.md.json'

    def tearDown(self):
        if os.path.isfile(self.tst_run_file): 
            os.remove(self.tst_run_file)
        pass

    def test_read_run(self):
        tst_run_container = self.service.read_run(self.ref_run_file)
        ref_run_container = create_run_metadata()
        self.assertEqual(ref_run_container.serialize(),
                         tst_run_container.serialize())

    def test_write_run(self):
        self.service.write_run(create_run_metadata(), self.tst_run_file)
        self.assertTrue(filecmp.cmp(self.tst_run_file, self.ref_run_file,
                                    shallow=False))