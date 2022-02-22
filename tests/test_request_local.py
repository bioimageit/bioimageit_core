import unittest
import os
import os.path

from bioimageit_core.plugins.data_local import LocalMetadataService


class TestRequestLocalFunctions(unittest.TestCase):

    def test_simplify_path1(self):
        sep = os.sep
        file = sep + 'my' + sep + 'computer' + sep + 'experiment' + sep \
            + 'svdeconv' + sep + '..' + sep + 'data' + sep + 'raw.md.json'
        simplified_file = LocalMetadataService.simplify_path(file)
        self.assertEqual(simplified_file,
                         sep + 'my' + sep + 'computer' + sep + 'experiment'
                         + sep + 'data' + sep + 'raw.md.json')

    def test_simplify_path2(self):
        sep = os.sep
        file = sep + 'my' + sep + 'computer' + sep + 'experiment' + sep \
               + 'svdeconv' + sep + 'denoise' + sep + '..' \
               + sep + '..' + sep + 'data' + sep + 'raw.md.json'
        simplified_file = LocalMetadataService.simplify_path(file)
        self.assertEqual(simplified_file,
                         sep + 'my' + sep + 'computer' + sep + 'experiment'
                         + sep + 'data' + sep + 'raw.md.json')

    def test_relative_path1(self):
        sep = os.sep
        reference_file = 'my' + sep + 'computer' + sep + 'experiment' + sep \
                         + 'data' + sep + 'rawdata.md.json'
        file = 'my' + sep + 'computer' + sep + 'experiment' + sep + 'data' \
               + sep + 'rawdata.tif'
        relative_file = LocalMetadataService.relative_path(file, reference_file)
        self.assertEqual(relative_file, 'rawdata.tif')

    def test_relative_path2(self):
        sep = os.sep
        reference_file = 'my' + sep + 'computer' + sep + 'experiment' + sep \
                         + 'svdeconv' + sep + 'processeddata.md.json'
        file = 'my' + sep + 'computer' + sep + 'experiment' + sep + 'data' \
               + sep + 'raw.md.json'
        relative_file = LocalMetadataService.relative_path(file, reference_file)
        self.assertEqual(relative_file,
                         '..' + sep + 'data' + sep + 'raw.md.json')

    def test_absolute_path(self):
        sep = os.sep
        reference_file = 'my' + sep + 'computer' + sep + 'experiment' + sep \
                         + 'data' + sep + 'rawdata.md.json'
        file = 'rawdata.tif'
        abs_file = LocalMetadataService.absolute_path(file, reference_file)
        self.assertEqual(abs_file,
                         'my' + sep + 'computer' + sep + 'experiment' + sep
                         + 'data' + sep + 'rawdata.tif')
