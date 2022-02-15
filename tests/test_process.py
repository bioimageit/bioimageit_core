import unittest
import os
import os.path

from bioimageit_core.core.config import ConfigAccess
from bioimageit_core.process import Process, ProcessAccess


class TestLocalProcess(unittest.TestCase):
    def setUp(self):
        self.xml_file = os.path.join('tests', 'test_processes_local', 'svdeconv', 'svdeconv2d.xml')
        ConfigAccess(os.path.join('tests', 'test_config','config_local.json'))

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
        self.xml_file = os.path.join('tests', 'test_processes_local', 'svdeconv', 'svdeconv2d.xml')
        ConfigAccess(os.path.join('tests', 'test_config', 'config_local.json'))

    def tearDown(self):
        ConfigAccess.__instance = None         

    def test_get_process(self):
        process = ProcessAccess().get('svdeconv2d_v0.1.0')
        self.assertEqual(process.metadata.uri, os.path.abspath(self.xml_file))     

    def test_get_process_categories1(self):
        categories = ProcessAccess().get_categories('root')
        self.assertEqual(len(categories), 6)

    def test_get_process_categories2(self):
        categories = ProcessAccess().get_categories('colocalization')
        self.assertEqual(len(categories), 2)   

    def test_get_category_processes1(self):
        processes = ProcessAccess().get_category_processes('Spots detection') 
        self.assertEqual(len(processes), 1)
