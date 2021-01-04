import unittest
import os
import os.path

from bioimageit_core.processes.service_local import LocalProcessService


class TestLocalMetadataService(unittest.TestCase):

    def setUp(self):
        self.service = LocalProcessService()
        self.xml_file = os.path.join('tests', 'test_processes_local', 'svdeconv', 'svdeconv2d.xml')
        self.xml_dir = os.path.join('tests', 'test_processes_local')
        self.service.xml_dirs.append(self.xml_dir)
        self.service.categories_json = \
            os.path.join('tests', 'test_processes_local', 'categories.json')
        self.service._load()
        
    def tearDown(self):
        pass

    def test_load_database(self):
        self.assertEqual(len(self.service.database), 5)

    def test_read_process(self):
        container = self.service.read_process(self.xml_file)
        t1 = False
        if container.name == 'SPARTION 2D':
            t1 = True
        t2 = False
        if container.version == '0.1.0':
            t2 = True
        t3 = False    
        if container.id == 'svdeconv2d':
            t3 = True
        self.assertTrue(t1*t2*t3) 

    def test_read_process_index(self):
        container = self.service.read_process_index(self.xml_file)
        t1 = False
        if container.name == 'SPARTION 2D':
            t1 = True
        t2 = False
        if container.version == '0.1.0':
            t2 = True
        t3 = False    
        if container.id == 'svdeconv2d':
            t3 = True
        self.assertTrue(t1*t2*t3)  

    def test_search1(self):
        result = self.service.search('deconv') 
        self.assertEqual(len(result), 2)

    def test_search2(self):
        result = self.service.search('wil') 
        self.assertEqual(len(result), 1) 

    def test_search3(self):
        result = self.service.search('') 
        self.assertEqual(len(result), 5)  

    def test_search4(self):
        result = self.service.search('azertyuiop') 
        self.assertEqual(len(result), 0)           

    def test_get_process(self):
        uri = self.service.get_process('svdeconv2d_v0.1.0')
        self.assertEqual(uri, os.path.abspath(self.xml_file))  

    def test_get_categories1(self):
        categories = self.service.get_categories('root')
        self.assertEqual(len(categories), 6)

    def test_get_categories2(self):
        categories = self.service.get_categories('colocalization')
        self.assertEqual(len(categories), 2)  

    def test_get_category_processes1(self):
        processes = self.service.get_category_processes('Spots detection') 
        self.assertEqual(len(processes), 1)
