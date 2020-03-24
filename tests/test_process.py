import unittest
import os
import os.path

from bioimagepy.process import Process

class TestLocalData(unittest.TestCase):
    def setUp(self):
        self.xml_file = 'tests/test_processes_local/svdeconv/svdeconv2d.xml'

    def tearDown(self):
        pass

    def test_process(self):
        process = Process(self.xml_file)
        t1 = False
        if process.metadata.name == 'SPARTION 2D':
            t1 = True
        t2 = False
        if process.metadata.version == '0.1.0':
            t2 = True
        t3 = False    
        if process.metadata.id == 'svdeconv2d':
            t3 = True
        self.assertTrue(t1*t2*t3) 