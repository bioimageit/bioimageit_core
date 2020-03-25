import unittest
import os
import os.path

from bioimagepy.config import ConfigAccess
from bioimagepy.process import Process, ProcessAccess

class TestLocalProcess(unittest.TestCase):
    def setUp(self):
        self.xml_file = 'tests/test_processes_local/svdeconv/svdeconv2d.xml'
        ConfigAccess('tests/test_config/config_local.json')

    def tearDown(self):
        ConfigAccess.__instance = None

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

class TestLocalProcessAccess(unittest.TestCase):        
    def setUp(self):
        self.xml_file = 'tests/test_processes_local/svdeconv/svdeconv2d.xml'
        ConfigAccess('tests/test_config/config_local.json')

    def tearDown(self):
        ConfigAccess.__instance = None         

    def test_get_process(self):
        process = ProcessAccess().get('svdeconv2d_v0.1.0')
        self.assertEqual(process.metadata.uri, self.xml_file)      