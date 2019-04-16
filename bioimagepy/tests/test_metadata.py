import unittest
from ..metadata.data import BiRawData
from ..metadata.dataset import BiDataSet

class TestBiRawData(unittest.TestCase):

    def setUp(self):
        self.mydata = BiRawData('bioimagepy/tests/data/file1.md.json')

    def test_read_rawdata_url(self):
        self.assertEqual(self.mydata.url(), 'celegans1.tif')

    def test_read_rawdata_name(self):
        self.assertEqual(self.mydata.metadata["common"]["name"], 'celegans1')

    def test_read_rawdata_author(self):
        self.assertEqual(self.mydata.metadata["common"]["author"], 'Sylvain Prigent')

    def test_read_rawdata_createddate(self):
        self.assertEqual(self.mydata.metadata["common"]["createddate"], '2019-02-12')    

    def test_read_rawdata_datatype(self):
        self.assertEqual(self.mydata.metadata["common"]["datatype"], 'image') 

    def test_read_rawdata_type(self):
        self.assertEqual(self.mydata.metadata["origin"]["type"], 'raw') 


class TestBiDataSet(unittest.TestCase):
    def setUp(self):
        self.mydataset = BiDataSet('bioimagepy/tests/data/rawdataset.md.json')

    def test_read_name(self):
        self.assertEqual(self.mydataset.name(), 'mydataset')  

    def test_read_size(self):
        self.assertEqual(self.mydataset.size(), 5)   

    def test_read_url0(self):
        self.assertEqual(self.mydataset.url(0), "file1.md.json")   

    def test_read_url4(self):
        self.assertEqual(self.mydataset.url(4), "file5.md.json")          

if __name__ == '__main__':
    unittest.main()