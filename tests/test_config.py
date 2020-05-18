import unittest
import os
import os.path
import filecmp

from bioimagepy.config import Config, ConfigAccess

class TestLocalData(unittest.TestCase):
    def setUp(self):
        self.config_local_file = 'tests/test_config/config_local.json'

    def tearDown(self):
        ConfigAccess.__instance = None  

    def _check_content(self, config):
        t1 = False
        if config['metadata']['service'] == 'LOCAL':
            t1 = True 
        t2 = False
        if config['process']['service'] == 'LOCAL':
            t2 = True   
        t3 = False
        if config['runner']['service'] == 'LOCAL':
            t3 = True  
        return t1*t2*t3    

    def test_read_config(self):
        config = Config(self.config_local_file) 
        self.assertTrue(self._check_content(config.config))

    def test_access(self):
        ConfigAccess(self.config_local_file) 
        content = ConfigAccess.instance().config
        self.assertTrue(self._check_content(content))              
