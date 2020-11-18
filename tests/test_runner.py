import unittest
import os
import os.path

from bioimageit_core.config import ConfigAccess
from bioimageit_core.process import Process
from bioimageit_core.runner import Runner


class TestLocalRunner(unittest.TestCase):
    def setUp(self):
        self.xml_file = 'tests/test_processes_local/helloworld.xml'
        self.tst_out_file = 'tests/test_processes_local/helloworld.txt'
        ConfigAccess('tests/test_config/config_local.json')

    def tearDown(self):
        ConfigAccess.__instance = None
        if os.path.isfile(self.tst_out_file):
            os.remove(self.tst_out_file)

    def test_exec(self):
        runner = Runner(Process(self.xml_file))
        message = "Hello World From test!"
        runner.exec("m", message, "o", self.tst_out_file)
        with open(self.tst_out_file, 'r') as content_file:
            content = content_file.read()
        self.assertEqual(content, message)
