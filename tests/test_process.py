import os
import unittest
from bioimagepy.process import BiProcess
 
class TestBiProcess(unittest.TestCase):

    def setUp(self):
        self.process = BiProcess('tests/data/process.xml')

    def test_run_process(self):
        outputFile = 'tests/data/process_result.txt'
        self.process.exec('-t', '"Hello world"', 
               '-o', outputFile) 

        with open(outputFile, 'r') as content_file:
            content = content_file.read()    
        content = content.replace('\n', '')    
        os.remove(outputFile)        

        self.assertEqual(content, 'Hello world')

    
