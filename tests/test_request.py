import unittest
import os
import os.path
import filecmp
import shutil

from bioimageit_core.api import Request
from bioimageit_core.containers import Run, ProcessedData
from bioimageit_core.core.serialize import (serialize_experiment, serialize_raw_data,
                                            serialize_processed_data, serialize_dataset,
                                            serialize_run)
from tests.metadata import (create_experiment, create_raw_data,
                            create_processed_data, create_dataset)


class TestRequest(unittest.TestCase):
    def setUp(self):
        self.request = Request(os.path.join('tests', 'config.json'))
        self.request.connect()
        self.ref_experiment_uri = \
            os.path.join('tests', 'test_metadata_local', 'experiment.md.json')
        self.test_experiment_uri = \
            os.path.join('tests', 'test_metadata_local',
                         'test_experiment.md.json')
        self.test_experiment_dir = \
            os.path.join('tests', 'test_metadata_local')
        self.test_import_image = \
            os.path.join('tests', 'test_images', 'data', 'population1_001.tif')
        self.test_import_dir = \
            os.path.join('tests', 'test_images', 'data')

        self.ref_rawdata_file = \
            os.path.join('tests', 'test_metadata_local', 'data', 'population1_001.md.json')
        self.tst_rawdata_file = \
            os.path.join('tests', 'test_metadata_local', 'data', 'population1_001_tst.md.json')
        self.ref_processeddata_file = \
            os.path.join('tests', 'test_metadata_local', 'process1', 'population1_001_o.md.json')
        self.tst_processeddata_file = \
            os.path.join('tests', 'test_metadata_local', 'process1', 'population1_001_o_tst.md.json')
        self.ref_processeddata2_file = \
            os.path.join('tests', 'test_metadata_local', 'process2', 'population1_001_o_o.md.json')

        self.ref_dataset_file = \
            os.path.join('tests', 'test_metadata_local', 'data',
                         'rawdataset.md.json')
        self.tst_dataset_file = \
            os.path.join('tests', 'test_metadata_local', 'data',
                         'rawdataset_tst.md.json')

        self.ref_run_file = \
            os.path.join('tests', 'test_metadata_local', 'process1',
                         'run.md.json')

    def tearDown(self):
        if os.path.isfile(self.test_experiment_uri):
            os.remove(self.test_experiment_uri)
        self._delete_experiment()
        if os.path.isfile(self.tst_rawdata_file):
            os.remove(self.tst_rawdata_file)
        if os.path.isfile(self.tst_processeddata_file):
            os.remove(self.tst_processeddata_file)
        #if os.path.isfile(self.ref_processeddata2_file):
        #    os.remove(self.ref_processeddata2_file)
        if os.path.isfile(self.tst_dataset_file):
            os.remove(self.tst_dataset_file)
        # pass

    def _delete_experiment(self):
        path = os.path.join(self.test_experiment_dir, 'myexperiment')
        if os.path.isdir(path):
            shutil.rmtree(path)

    def test_create_experiment(self):
        self.request.create_experiment("myexperiment", "sprigent", date='now',
                                       keys=["key1", "key2"],
                                       destination=self.test_experiment_dir)

        t1 = os.path.isdir(os.path.join(self.test_experiment_dir,
                                        'myexperiment'))
        t2 = os.path.isfile(os.path.join(self.test_experiment_dir,
                                         'myexperiment',
                                         'experiment.md.json'))
        t3 = os.path.isdir(os.path.join(self.test_experiment_dir,
                                        'myexperiment', 'data'))
        t4 = os.path.isfile(os.path.join(self.test_experiment_dir,
                                         'myexperiment', 'data',
                                         'raw_dataset.md.json'))
        self.assertTrue(t1 * t2 * t3 * t4)

    def test_get_experiment(self):
        experiment = self.request.get_experiment(self.ref_experiment_uri)
        ref_experiment = create_experiment()
        # print(serialize_experiment(experiment))
        # print(serialize_experiment(ref_experiment))

        self.assertEqual(serialize_experiment(experiment),
                         serialize_experiment(ref_experiment))

    def test_update_experiment(self):
        experiment = create_experiment()
        experiment.md_uri = self.test_experiment_uri
        # print(serialize_experiment(experiment))
        self.request.update_experiment(experiment)

        self.assertTrue(filecmp.cmp(self.test_experiment_uri,
                                    self.ref_experiment_uri, shallow=False))

    def test_import_data(self):
        experiment = self.request.create_experiment("myexperiment", "sprigent",
                                                    date='now', keys=[],
                                                    destination=self.test_experiment_dir)
        data_path = self.test_import_image
        name = 'population1_001.tif'
        author = 'sprigent'
        format_ = 'imagetiff'
        tags = {"Population": "population1", "ID": "001"}
        rawData = self.request.import_data(experiment, data_path, name, author,
                                           format_, date='now', key_value_pairs=tags)
        # test generated files
        t1 = os.path.isfile(os.path.join(self.test_experiment_dir,
                                         'myexperiment',
                                         'data',
                                         'population1_001.md.json'))
        t2 = False
        if rawData.name == 'population1_001.tif':
            t2 = True
        t3 = os.path.isfile(os.path.join(self.test_experiment_dir,
                                         'myexperiment',
                                         'data',
                                         'population1_001.tif'))
        t4 = False
        if rawData.key_value_pairs['Population'] == 'population1':
            t4 = True
        t5 = False
        if 'Population' in experiment.keys:
            t5 = True
        self.assertTrue(t1 * t2 * t3 * t4 * t5)

    def test_import_dir(self):
        experiment = self.request.create_experiment("myexperiment", "sprigent",
                                                    date='now', keys=[],
                                                    destination=self.test_experiment_dir)
        self.request.import_dir(experiment, self.test_import_dir,
                                filter_=r'\.tif$', author='sprigent',
                                format_='imagetiff', date='now')

        data_dir = os.path.join(self.test_experiment_dir, 'myexperiment',
                                'data')
        data_files = next(os.walk(data_dir))[2]  # to count files in data dir
        # count the number of imported files
        t1 = False
        if len(data_files) == 81:
            t1 = True
        # count the number of lines in the rawdataset.md.json file
        t2 = False
        fd = open(os.path.join(data_dir, 'raw_dataset.md.json'))
        number_of_lines = len(fd.readlines())
        fd.close()
        if number_of_lines == 166:
            t2 = True
        self.assertTrue(t1*t2)

    def test_tag_from_name(self):
        experiment = self.request.create_experiment("myexperiment", "sprigent",
                                                    date='now', keys=[],
                                                    destination=self.test_experiment_dir)
        self.request.import_dir(experiment, self.test_import_dir,
                                filter_=r'\.tif$', author='sprigent',
                                format_='imagetiff', date='now')

        self.request.annotate_from_name(experiment, 'Population',
                                   ['population1', 'population2'])
        # test if tag Population in the experiment metadata
        t1 = False
        if 'Population' in experiment.keys:
            t1 = True
        # test few images tags
        data1 = self.request.get_raw_data(os.path.join(self.test_experiment_dir,
                                                       "myexperiment",
                                                       'data',
                                                       'population1_012.md.json')
                                          )
        t2 = False
        if 'Population' in data1.key_value_pairs and \
                data1.key_value_pairs['Population'] == 'population1':
            t2 = True
        data2 = self.request.get_raw_data(os.path.join(self.test_experiment_dir,
                                                      "myexperiment",
                                                      'data',
                                                      'population2_011.md.json')
                                         )
        t3 = False
        if 'Population' in data2.key_value_pairs and \
                data2.key_value_pairs['Population'] == 'population2':
            t3 = True
        self.assertTrue(t1 * t2 * t3)

    def test_tag_using_separator(self):
        experiment = self.request.create_experiment("myexperiment", "sprigent",
                                                    date='now', keys=[],
                                                    destination=self.test_experiment_dir)
        self.request.import_dir(experiment, self.test_import_dir,
                                filter_=r'\.tif$', author='sprigent',
                                format_='imagetiff', date='now')

        self.request.annotate_using_separator(experiment, 'ID', '_', 1)
        # test if tag ID in the experiment metadata
        t1 = False
        if 'ID' in experiment.keys:
            t1 = True
        # test few images tags
        data1 = self.request.get_raw_data(os.path.join(self.test_experiment_dir,
                                                      "myexperiment",
                                                      'data',
                                                      'population1_012.md.json'
                                                      ))
        t2 = False
        if 'ID' in data1.key_value_pairs and data1.key_value_pairs['ID'] == '012':
            t2 = True
        data2 = self.request.get_raw_data(os.path.join(self.test_experiment_dir,
                                                      "myexperiment",
                                                      'data',
                                                      'population2_011.md.json'
                                                      ))
        t3 = False
        if 'ID' in data2.key_value_pairs and data2.key_value_pairs['ID'] == '011':
            t3 = True
        self.assertTrue(t1*t2*t3)

    def test_get_raw_data(self):
        raw_data_read = self.request.get_raw_data(self.ref_rawdata_file)
        raw_data_ref = create_raw_data()
        self.assertEqual(serialize_raw_data(raw_data_read),
                         serialize_raw_data(raw_data_ref))

    def test_update_raw_data(self):
        raw_data = create_raw_data()
        raw_data.md_uri = self.tst_rawdata_file
        self.request.update_raw_data(raw_data)
        self.assertTrue(filecmp.cmp(self.tst_rawdata_file,
                                    self.ref_rawdata_file,
                                    shallow=False))

    def test_get_processed_data(self):
        processed_data_read = self.request.get_processed_data(
            self.ref_processeddata_file)
        processed_data_ref = create_processed_data()
        self.assertEqual(serialize_processed_data(processed_data_read),
                         serialize_processed_data(processed_data_ref))

    def test_update_processed_data(self):
        processed_data = create_processed_data()
        processed_data.md_uri = self.tst_processeddata_file
        self.request.update_processed_data(processed_data)
        self.assertTrue(filecmp.cmp(self.tst_processeddata_file,
                                    self.ref_processeddata_file,
                                    shallow=False))

    def test_get_dataset_from_uri(self):
        ref_dataset = create_dataset()
        read_dataset = self.request.get_dataset_from_uri(self.ref_dataset_file)
        self.assertEqual(serialize_dataset(ref_dataset),
                         serialize_dataset(read_dataset))

    def test_update_dataset(self):
        container = create_dataset()
        container.md_uri = self.tst_dataset_file
        self.request.update_dataset(container)
        self.assertTrue(filecmp.cmp(self.tst_dataset_file,
                                    self.ref_dataset_file,
                                    shallow=False))

    def test_get_raw_dataset(self):
        experiment = self.request.get_experiment(self.ref_experiment_uri)
        read_dataset = self.request.get_dataset(experiment, 'data')
        ref_dataset = create_dataset()
        self.assertEqual(serialize_dataset(ref_dataset),
                         serialize_dataset(read_dataset))

    def test_get_parent(self):
        processed_data = self.request.get_processed_data(
            self.ref_processeddata2_file)
        parent_data = self.request.get_parent(processed_data)
        self.assertEqual(parent_data.name, 'population1_001_o')

    def test_get_origin(self):
        processed_data = self.request.get_processed_data(
            self.ref_processeddata2_file)
        parent_data = self.request.get_origin(processed_data)
        self.assertEqual(parent_data.name, 'population1_001.tif')

    def test_get_dataset_raw(self):
        experiment = self.request.get_experiment(self.ref_experiment_uri)
        dataset = self.request.get_dataset(experiment, "data")
        self.assertEqual(dataset.name, 'data')

    def test_get_dataset_processed(self):
        experiment = self.request.get_experiment(self.ref_experiment_uri)
        dataset = self.request.get_dataset(experiment, "process1")
        self.assertEqual(dataset.name, 'process1')

    def test_get_data(self):
        experiment = self.request.get_experiment(self.ref_experiment_uri)
        dataset = self.request.get_dataset(experiment, "process1")
        data = self.request.get_data(dataset, query='name=population1_001_o',
                                     origin_output_name='o')
        self.assertEqual(data[0].name, 'population1_001_o')

    def test_create_dataset(self):
        experiment = self.request.create_experiment("myexperiment", "sprigent",
                                                    date='now', keys=[],
                                                    destination=self.test_experiment_dir)

        self.request.create_dataset(experiment, "myprocess")

        t1 = False
        dataset_file = os.path.join(self.test_experiment_dir, "myexperiment",
                                    "myprocess", "processed_dataset.md.json")
        if os.path.isfile(dataset_file):
            t1 = True

        t2 = False
        dataset = self.request.get_dataset(experiment, "myprocess")
        if dataset.name == "myprocess":
            t2 = True
        self.assertTrue(t1*t2)

    def test_create_run(self):
        experiment = self.request.create_experiment("myexperiment", "sprigent",
                                                    date='now', keys=[],
                                                    destination=self.test_experiment_dir)

        dataset = self.request.create_dataset(experiment, "threshold")
        run_info = Run()
        run_info.set_process(name='threshold', uri='uniqueIdOfMyAlgorithm')
        run_info.add_input(name='image', dataset='data',
                           query="Population=Population1")
        run_info.add_parameter('threshold', '100')
        self.request.create_run(dataset, run_info)

        t1 = False
        run_file = os.path.join(self.test_experiment_dir, "myexperiment",
                                "threshold", "run.md.json")
        if os.path.isfile(run_file):
            t1 = True

        t2 = False
        if run_info.process_name == "threshold":
            t2 = True

        self.assertTrue(t1*t2)

    def test_get_run(self):
        run = self.request.get_run(self.ref_run_file)
        t1 = False
        if run.process_name == "SPARTION 2D":
            t1 = True
        t2 = False
        if run.processed_dataset.uuid == "fake_uuid":
            t2 = True
        self.assertTrue(t1*t2)

    def test_create_data(self):
        experiment = self.request.create_experiment("myexperiment", "sprigent",
                                                    date='now', keys=[],
                                                    destination=self.test_experiment_dir)
        self.request.import_dir(experiment, self.test_import_dir,
                                filter_=r'\.tif$', author='sprigent',
                                format_='imagetiff', date='now')

        raw_dataset = self.request.get_dataset(experiment, "data")

        raw_data = self.request.get_data(raw_dataset, query="name=population1_001")[0]

        dataset = self.request.create_dataset(experiment, "threshold")
        run_info = Run()
        run_info.set_process(name='threshold', uri='uniqueIdOfMyAlgorithm')
        run_info.add_input(name='image', dataset='data',
                           query="Population=Population1")
        run_info.add_parameter('threshold', '100')
        self.request.create_run(dataset, run_info)
        processed_data = ProcessedData()
        output_image_path = os.path.abspath(os.path.join(
                                         self.test_experiment_dir,
                                         "myexperiment", "threshold",
                                         "o_"+raw_data.name+'.tif'))
        processed_data.set_info(name="myimage", author="sprigent", date='now',
                                format_="imagetiff", url=output_image_path)
        processed_data.add_input(id_="i", data=raw_data)
        processed_data.set_output(id_="o", label="threshold")

        processed_data = self.request.create_data(dataset, run_info, processed_data)

        t1 = False
        if os.path.isfile(processed_data.md_uri):
            t1 = True
        t2 = False
        if processed_data.name == "myimage":
            t2 = True
        t3 = False
        if "myimage.tif" in processed_data.uri:
            t3 = True
        t4 = False
        if "run.md.json" in processed_data.run.md_uri:
            t4 = True

        self.assertTrue(t1*t2*t3*t4)
