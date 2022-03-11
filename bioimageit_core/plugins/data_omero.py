# -*- coding: utf-8 -*-
"""bioimageit_core OMERO metadata service.

This module implements the OMERO service for metadata
(Data, DataSet and Experiment) management.
This OMERO service read/write and query metadata from an OMERO database

Classes
------- 
OmeroMetadataServiceBuilder
OmeroMetadataService

"""
import numpy as np
import os
import os.path
import json
import re

from skimage.io import imread
from omero.gateway import BlitzGateway, DatasetWrapper, ProjectWrapper
import omero

from bioimageit_formats import FormatsAccess, formatsServices

from bioimageit_core.core.config import ConfigAccess
from bioimageit_core.core.utils import generate_uuid
from bioimageit_core.core.exceptions import DataServiceError
from bioimageit_core.containers.data_containers import (METADATA_TYPE_RAW,
                                                        METADATA_TYPE_PROCESSED,
                                                        Container,
                                                        RawData,
                                                        ProcessedData,
                                                        ProcessedDataInputContainer,
                                                        Dataset,
                                                        Experiment,
                                                        Run,
                                                        RunInputContainer,
                                                        RunParameterContainer,
                                                        DatasetInfo,
                                                        )


class OmeroMetadataServiceBuilder:
    """Service builder for the metadata service"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = OmeroMetadataService()
        return self._instance


class OmeroMetadataService:
    """Service for local metadata management"""

    def __init__(self, host, port, username, password):
        self.service_name = 'OmeroMetadataService'
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._conn = BlitzGateway(self._username, self._password,
                                 host=self._host, port=self._port,
                                 secure=True)

    @staticmethod
    def _read_json(md_uri: str):
        """Read the metadata from the a json file"""
        if os.path.getsize(md_uri) > 0:
            with open(md_uri) as json_file:
                return json.load(json_file)

    @staticmethod
    def _write_json(metadata: dict, md_uri: str):
        """Write the metadata to the a json file"""
        with open(md_uri, 'w') as outfile:
            json.dump(metadata, outfile, indent=4)

    def _omero_connect(self):
        rv = self._conn.connect()
        if not rv:
            raise DataServiceError(
                'Unable to connect to the Omero database'
            )

    def _omero_close(self):
        self._conn.close()

    def _omero_is_project(self, name):
        """Check is a project 

        Parameters
        ----------
        name: str
            Name of the project

        Returns
        -------
        True if a project with this name exists, False otherwise

        """
        value = False
        self._omero_connect()
        try:
            projects = self._conn.getObjects("Project")
            for project in projects:
                if project.name == name:
                    value = True
        finally: 
            self._omero_close()
            return value     

    def _omero_write_tiff_image(self, data_path, image_name, parent_dataset):
        numpy_image = [imread(data_path)]
        # TODO manage other image sizes
        size_z = 1
        size_c = 1
        size_t = 1

        def plane_gen():
            """generator will yield planes"""
            for p in numpy_image:
                yield p

        i = self.conn.createImageFromNumpySeq(plane_gen(), image_name, 
                                              size_z, size_c, size_t, 
                                              description='',
                                              dataset=parent_dataset)  

    def create_experiment(self, name, author, date='now', keys=None,
                          destination=''):
        """Create a new experiment

        Parameters
        ----------
        name: str
            Name of the experiment
        author: str
            username of the experiment author
        date: str
            Creation date of the experiment
        keys: list
            List of keys used for the experiment vocabulary
        destination: str
            Destination where the experiment is created. It is a the path of the
            directory where the experiment will be created for local use case

        Returns
        -------
        Experiment container with the experiment metadata

        """
        if keys is None:
            keys = []
        container = Experiment()
        container.uuid = None
        container.name = name
        container.author = author
        container.date = date
        container.keys = keys

        self._omero_connect()
        try:
            # check if the experiment already exists
            projects = self._conn.getObjects("Project")
            for project in projects:
                if project.name == name:
                    raise DataServiceError('Cannot create Experiment: a project with the same name '
                                           'already already exists in the Omero database')

            # create the project    
            new_project = ProjectWrapper(self._conn, omero.model.ProjectI())
            new_project.setName(name)
            new_project.setDescription('')
            new_project.save()
            project_obj = new_project._obj  
            container.uuid = project_obj.id

            # create an empty raw dataset
            new_dataset = DatasetWrapper(self._conn, omero.model.DatasetI())
            new_dataset.setName('data')
            new_dataset.save()
            dataset_obj = new_dataset._obj
        
            # link dataset to project
            link = omero.model.ProjectDatasetLinkI()
            link.setChild(omero.model.DatasetI(dataset_obj.id.val, False))
            link.setParent(omero.model.ProjectI(project_obj, False))
            self._conn.getUpdateService().saveObject(link)                        

            # add keys as Omero tags
            for tag in keys:
                tag_ann = omero.gateway.TagAnnotationWrapper(self._conn)
                tag_ann.setValue(tag)
                tag_ann.save()
                project_obj.linkAnnotation(tag_ann)
        finally: 
            self._omero_close()      
        return container

    def get_workspace_experiments(self, workspace_uri = ''):
        """Read the experiments in the user workspace

        Parameters
        ----------
        workspace_uri: str
            URI of the workspace

        Returns
        -------
        list of experiment containers  
          
        """
        self._omero_connect()
        experiments = []
        try:
            projects = self._conn.getObjects("Project")
            for project in projects:
                container = Experiment()
                container.uuid = project.id
                container.name = project.name
                container.author = project.owner
                container.date = project.date
                container.keys = {}
                experiments.append({'md_uri': project.id, 'info': container})
        finally: 
            self._omero_close() 
        return experiments    

    def get_experiment(self, md_uri):
        """Read an experiment from the database

        Parameters
        ----------
        md_uri: str
            URI of the experiment. For local use case, the URI is either the
            path of the experiment directory, or the path of the
            experiment.md.json file

        Returns
        -------
        Experiment container with the experiment metadata

        """
        self._omero_connect()
        container = Experiment()
        try:
            project = self._conn.getObject("Project", md_uri)
            if project is None:
                raise DataServiceError('Cannot find the experiment metadata from the given URI')
            container.uuid = project.id    
            container.md_uri = project.id
            container.name = project.name
            container.author = project.owner
            container.date = project.date
            # get the tags
            for ann in project.listAnnotations():
                if ann.OMERO_TYPE == omero.model.TagAnnotationI:
                    container.keys.append(ann.getValue())

            # get all the datasets
            for dataset in project.listChildren():
                if dataset.name == 'data':
                    container.raw_dataset = DatasetInfo(dataset.name,
                                                        dataset.id,
                                                        dataset.id)
                else:
                    container.processed_datasets.append(DatasetInfo(dataset.name,
                                                                    dataset.id,
                                                                    dataset.id)
                                                        )
        finally: 
            self._omero_close() 
        return container  

    def update_experiment(self, experiment):
        """Write an experiment to the database

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata

        """
        self._omero_connect()
        try:
            # set the main info
            project = self._conn.getObject("Project", experiment.md_uri)
            project.name = experiment.name
            project.owner = experiment.owner
            project.data = experiment.date
            project.save()
            # set the tags
            # delete tags in the OMERO database and not in the keys list
            to_delete = []
            existing_tags = []
            for ann in project.listAnnotations():
                if ann.OMERO_TYPE == omero.model.TagAnnotationI and ann.getValue() not in experiment.keys:
                    to_delete.append(ann.id)
                else:
                    existing_tags.append(ann.getValue())    
            self._conn.deleteObjects('Annotation', to_delete, wait=True)
            # add not existing tags
            for key in experiment.keys:
                if key not in existing_tags:
                    tag_ann = omero.gateway.TagAnnotationWrapper(self._conn)
                    tag_ann.setValue(key)
                    tag_ann.save()
                    project.linkAnnotation(tag_ann)
        finally:
            self._omero_close()

    def import_data(self, experiment, data_path, name, author, format_,
                    date='now', key_value_pairs=dict):
        """import one data to the experiment

        The data is imported to the raw dataset

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        data_path: str
            Path of the accessible data on your local computer
        name: str
            Name of the data
        author: str
            Person who created the data
        format_: str
            Format of the data (ex: tif)
        date: str
            Date when the data where created
        key_value_pairs: dict
            Dictionary {key:value, key:value} to annotate files

        Returns
        -------
        class RawData containing the metadata

        """
        self._omero_connect()
        try:
            # get the raw dataset
            raw_dataset_id = os.path.abspath(experiment.raw_dataset.url)
            dataset = self._conn.getObject("Dataset", raw_dataset_id)

            # copy the image to omero
            image_id = 0
            if format_ == 'imagetiff':
                image_id = self._omero_write_tiff_image(data_path, name, dataset)
            else:
                raise DataServiceError(f'OMERO service can only import tiff images (format={format_})')  

            # add key value pairs
            keys_value_list = []
            for key, value in key_value_pairs.items():
                keys_value_list.append([key, value])
            if len(keys_value_list) > 0:
                map_ann = omero.gateway.MapAnnotationWrapper(self._conn)
                namespace = omero.constants.metadata.NSCLIENTMAPANNOTATION
                map_ann.setNs(namespace)
                map_ann.setValue(keys_value_list)
                map_ann.save()
                image = self._conn.getObject("Image", image_id)
                image.linkAnnotation(map_ann)      
        finally:
            self._omero_close()    

        # create the container
        metadata = RawData()
        metadata.uuid = image_id
        metadata.md_uri = image_id
        metadata.name = name
        metadata.author = author
        metadata.format = format_
        metadata.date = date
        metadata.key_value_pairs = key_value_pairs

        return metadata

    def import_dir(self, experiment, dir_uri, filter_, author, format_, date,
                   directory_tag_key='', observers=None):
        """Import data from a directory to the experiment

        This method import with or without copy data contained
        in a local folder into an experiment. Imported data are
        considered as RawData for the experiment

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        dir_uri: str
            URI of the directory containing the data to be imported
        filter_: str
            Regular expression to filter which files in the folder
            to import
        author: str
            Name of the person who created the data
        format_: str
            Format of the image (ex: tif)
        date: str
            Date when the data where created
        directory_tag_key
            If the string directory_tag_key is not empty, a new tag key entry with the
            key={directory_tag_key} and the value={the directory name}.
        observers: list
            List of observers to notify the progress

        """
        files = os.listdir(dir_uri)
        count = 0
        key_value_pairs = {}
        if directory_tag_key != '':
            key_value_pairs[directory_tag_key] = os.path.dirname(dir_uri)

        if format_ == 'imagetiff':
            for file in files:
                count += 1
                r1 = re.compile(filter_)
                if r1.search(file):
                    if observers is not None:
                        for obs in observers:
                            obs.notify_progress(int(100 * count / len(files)), file)
                    self.import_data(experiment, os.path.join(dir_uri, file), file, author,
                                     format_, date, key_value_pairs)
        else:
            raise DataServiceError(f'OMERO service can only import tiff images (format={format_})')                                 

    def get_raw_data(self, md_uri):
        """Read a raw data from the database

        Parameters
        ----------
        md_uri: str
            URI if the raw data
        Returns
        -------
        RawData object containing the raw data metadata

        """
        container = RawData()
        self._omero_connect()
        try:
            # read base info
            image = self._conn.getObject("Image", md_uri)
            container.uuid = md_uri
            container.md_uri = md_uri
            container.uri = md_uri
            container.type = 'raw'
            container.name = image.name
            container.author = image.getDetails().getOwner().getOmeName()
            container.date = image.date
            container.format = 'imagetiff'

            # read metadata
            # TODO 

            # read key-value pairs
            for ann in image.listAnnotations():
                if ann.OMERO_TYPE == omero.model.MapAnnotationI:
                    values = ann.getValue()
                    for value in values:
                        container.key_value_pairs[value[0]] = value[1] 
            # read experiment tags if not in key_value_pairs
            project = self.conn.getObject('Project', image.getParent().getParent())
            for ann in project.listAnnotations():
                if ann.OMERO_TYPE == omero.model.TagAnnotationI:
                    if ann.getValue() not in container.key_value_pairs.keys():
                        container.key_value_pairs[ann.getValue()] = ''           
        finally:
            self._omero_close()
        return container

    def update_raw_data(self, raw_data):
        """Read a raw data from the database

        Parameters
        ----------
        raw_data: RawData
            Container with the raw data metadata

        """

        self._omero_connect()
        try:
            image = self._conn.getObject("Image", raw_data.md_uri)     
            image.name = raw_data.name 
            #image.owner = raw_data.author  
            image.date = raw_data.date 
            #image.format = raw_data.format
            image.save()

            # set the key value pairs
            # delete key in the OMERO database and not in the data keys list
            to_delete = []
            existing_tags = []
            keys = raw_data.key_value_pairs.keys()
            for ann in image.listAnnotations():
                if ann.OMERO_TYPE == omero.model.MapAnnotationI and ann.getValue()[0] not in keys:
                    to_delete.append(ann.id)
                else:
                    key_ = ann.getValue()[0]
                    ann.setValue([key_, raw_data.key_value_pairs[key_]])
                    existing_tags.append(ann.getValue()[0])    
            self._conn.deleteObjects('Annotation', to_delete, wait=True)
            # add not existing tags
            for key in keys:
                if key not in existing_tags:
                    map_ann = omero.gateway.MapAnnotationWrapper(self._conn)
                    map_ann.setValue([key, raw_data.key_value_pairs[key]])
                    map_ann.save()
                    image.linkAnnotation(map_ann)
        finally:
            self._omero_close()

    def _omero_download_image_md_attachments(self, image, destination_path):
        """Set an attachment file to an image

        Parameters
        ----------
        image: omero.Image
            Omero image container
        destination_path: str
            Path where the file is downloaded    

        """
        md_found = False
        for ann in image.listAnnotations():
            if isinstance(ann, omero.gateway.FileAnnotationWrapper):
                print("File ID:", ann.getFile().getId(), ann.getFile().getName(), \
                    "Size:", ann.getFile().getSize())
                if ann.getFile().getName().endswith('.md.json'):  
                    md_found = True  
                    file_path = os.path.join(destination_path, ann.getFile().getName())
                    with open(str(file_path), 'wb') as f:
                        print("\nDownloading file to", file_path, "...")
                        for chunk in ann.getFileInChunks():
                            f.write(chunk)
                    print("File downloaded!")
        if not md_found:
            raise DataServiceError('Cannot found the metadata file for image:', image.name)            

    def get_processed_data(self, md_uri):
        """Read a processed data from the database

        Parameters
        ----------
        md_uri: str
            URI if the processed data

        Returns
        -------
        ProcessedData object containing the raw data metadata

        """
        # read the data info
        self._omero_connect()
        try:
            image = self._conn.getObject("Image", md_uri) 
            if image is not None:
                container = ProcessedData()
                container.uuid = image.id
                container.md_uri = image.id
                container.name = image.name
                container.author = image.getDetails().getOwner().getOmeName()
                container.date = image.date
                container.format = 'imagetiff' # only image tif 2D gray works now
                container.uri = image.id

                md_json_file = os.path.join(ConfigAccess.instance().config['workspace'], 'processed_data.md.json')    
                self._omero_download_image_md_attachments(image, md_json_file)

                metadata = self._read_json(md_json_file)
                container.run = Container(metadata['origin']['run']["url"], metadata['origin']['run']["uuid"])
                # origin input
                for input_ in metadata['origin']['inputs']:
                    container.inputs.append(
                        ProcessedDataInputContainer(
                            input_['name'],
                            input_['url'],
                            input_['uuid'],
                            input_['type'],
                        )
                    )
                # origin output
                if 'name' in metadata['origin']['output']:
                    container.output['name'] = metadata['origin']['output']["name"]
                if 'label' in metadata['origin']['output']:
                    container.output['label'] = \
                        metadata['origin']['output']['label']

                return container
            else:
                return None   

        finally:
            self._omero_close()

    def update_processed_data(self, processed_data):
        """Read a processed data from the database

        Parameters
        ----------
        processed_data: ProcessedData
            Container with the processed data metadata

        """
        self._omero_connect()
        try:
            image = self._conn.getObject("Image", processed_data.md_uri)     
            image.name = processed_data.name 
            #image.owner = raw_data.author  
            image.date = processed_data.date 
            #image.format = raw_data.format
            image.save()

            # change the attachament file
            # write tmp md.json file
            # origin type
            metadata = dict()
            metadata['origin'] = dict()
            metadata['origin']['type'] = METADATA_TYPE_PROCESSED
            # run url
            metadata['origin']['run'] = {"url": processed_data.run.md_uri,
                                         "uuid": processed_data.run.uuid}
            # origin inputs
            metadata['origin']['inputs'] = list()
            for input_ in processed_data.inputs:
                metadata['origin']['inputs'].append(
                    {
                        'name': input_.name,
                        'url': input_.uri,
                        'uuid': input_.uuid,
                        'type': input_.type,
                    }
                )
            # origin output
            metadata['origin']['output'] = {
                'name': processed_data.output['name'],
                'label': processed_data.output['label'],
            }

            md_json_file = os.path.join(ConfigAccess.instance().config['workspace'], 'processed_data.md.json')
            self._write_json(metadata, md_json_file)

            # set the json file as attachment
            to_delete = []
            for ann in image.listAnnotations():
                if isinstance(ann, omero.gateway.FileAnnotationWrapper) and ann.getFile().getName() == 'processed_data.md.json':
                    to_delete.append(ann.id)
            self._conn.deleteObjects('Annotation', to_delete, wait=True)
            file_ann = self.conn.createFileAnnfromLocalFile(md_json_file, mimetype="text/plain", ns='', desc=None)
            image.linkAnnotation(file_ann)

        finally:
            self._omero_close()

    def get_dataset(self, md_uri):
        """Read a dataset from the database using it URI

        Parameters
        ----------
        md_uri: str
            URI if the dataset

        Returns
        -------
        Dataset object containing the dataset metadata

        """

        self._omero_connect()
        try:
            dataset = self.conn.getObject('Dataset', md_uri)
            if dataset is not None:
                container = Dataset()
                container.uuid = dataset.id
                container.md_uri = dataset.id
                container.name = dataset.name
                for image in dataset.listChildren():
                    container.uris.append(Container(image.id, image.id))
            else:
                raise DataServiceError('Dataset not found')
        finally:
            self._omero_close()        

    def update_dataset(self, dataset):
        """Read a processed data from the database

        Parameters
        ----------
        dataset: Dataset
            Container with the dataset metadata

        """
        self._omero_connect()
        try:
            dataset = self._conn.getObject('Dataset', dataset.md_uri)
            dataset.name = dataset.name
            dataset.save()
        finally:
            self._omero_close()

    def create_dataset(self, experiment, dataset_name):
        """Create a processed dataset in an experiment

        Parameters
        ----------
        experiment: Experiment
            Object containing the experiment metadata
        dataset_name: str
            Name of the dataset

        Returns
        -------
        Dataset object containing the new dataset metadata

        """
        self._omero_connect()
        try:
            # create dataset
            new_dataset = DatasetWrapper(self.conn, omero.model.DatasetI())
            new_dataset.setName(dataset_name)
            new_dataset.save()
            dataset_obj = new_dataset._obj
            
            # link dataset to project
            link = omero.model.ProjectDatasetLinkI()
            link.setChild(omero.model.DatasetI(dataset_obj.id.val, False))
            link.setParent(omero.model.ProjectI(experiment.md_uri, False))
            self._conn.getUpdateService().saveObject(link)

            container = Dataset()
            container.uuid = new_dataset.id
            container.md_uri = new_dataset.id
            container.name = new_dataset.name
            return container
        finally:
            self._omero_close()

    def create_run(self, dataset, run_info):
        """Create a new run metadata

        Parameters
        ----------
        dataset: Dataset
            Object of the dataset metadata
        run_info: Run
            Object containing the metadata of the run. md_uri is ignored and
            created automatically by this method

        Returns
        -------
        Run object with the metadata and the new created md_uri

        """
        self._omero_connect()
        try:
            omero_dataset = self._conn.getObject('Dataset', dataset.md_uri)

            # create the run annotation file
            ann_files = []
            for ann in omero_dataset.listAnnotations():
                if isinstance(ann, omero.gateway.FileAnnotationWrapper):
                    ann_files.append(ann.getFile().getName())

            run_md_file_name = "run.md.json"
            run_id_count = 0
            while run_md_file_name in ann_files:
                run_id_count += 1
                run_md_file_name = "run_" + str(run_id_count) + ".md.json" 

            file_path = os.path.join(ConfigAccess.instance().config['workspace'], run_md_file_name)
            run_info.processed_dataset = dataset
            run_info.uuid = ''
            run_info.md_uri = ''
            self._write_run(run_info, file_path)

            # upload the annotation file to the dataset
            file_ann = self._conn.createFileAnnfromLocalFile(file_path, mimetype="text/plain", ns='', desc=None)
            omero_dataset.linkAnnotation(file_ann)     # link it to dataset.

            run_info.uuid = file_ann.id
            run_info.md_uri = file_ann.id
            return run_info

        finally:
            self._omero_close()

    def get_run(self, md_uri):
        """Read a run metadata from the data base

        Parameters
        ----------
        md_uri
            URI of the run entry in the database

        Returns
        -------
        Run: object containing the run metadata

        """
        self._omero_connect()
        try:
            # copy the file from OMERO
            ann = self._conn.getObject('FileAnnotation', md_uri)
            print("File ID:", ann.getFile().getId(), ann.getFile().getName(), \
                    "Size:", ann.getFile().getSize())

            destination_path = os.path.join(ConfigAccess.instance().config('workspace'), 'run.md.json')        
            file_path = os.path.join(destination_path, ann.getFile().getName())
            with open(str(file_path), 'wb') as f:
                print("\nDownloading file to", file_path, "...")
                for chunk in ann.getFileInChunks():
                    f.write(chunk)
            print("File downloaded!")

            # read the file content 
            metadata = self._read_json(md_uri)
            container = Run()
            container.uuid = metadata['uuid']
            container.md_uri = md_uri
            container.process_name = metadata['process']['name']
            container.process_uri =  metadata['process']['url']
            container.processed_dataset = Container(
                metadata['processed_dataset']['url'],
                metadata['processed_dataset']['uuid']
            )
            for input_ in metadata['inputs']:
                container.inputs.append(
                    RunInputContainer(
                        input_['name'],
                        input_['dataset'],
                        input_['query'],
                        input_['origin_output_name'],
                    )
                )
            for parameter in metadata['parameters']:
                container.parameters.append(
                    RunParameterContainer(parameter['name'], parameter['value'])
                )
            return container
        finally:
            self._omero_close()

    def _write_run(self, run):
        """Write a run metadata to the data base

        Parameters
        ----------
        run
            Object containing the run metadata

        """
        metadata = dict()
        metadata['uuid'] = run.uuid

        metadata['process'] = {}
        metadata['process']['name'] = run.process_name
        metadata['process']['url'] = run.process_uri
        metadata['processed_dataset'] = {"uuid": run.processed_dataset.uuid,
                                         "url": run.processed_dataset.md_uri}
        metadata['inputs'] = []
        for input_ in run.inputs:
            metadata['inputs'].append(
                {
                    'name': input_.name,
                    'dataset': input_.dataset,
                    'query': input_.query,
                    'origin_output_name': input_.origin_output_name,
                }
            )
        metadata['parameters'] = []
        for parameter in run.parameters:
            metadata['parameters'].append(
                {'name': parameter.name, 'value': parameter.value}
            )

        self._write_json(metadata, run.md_uri)

    def create_data(self, dataset, run, processed_data):
        """Create a new processed data for a given dataset

        Parameters
        ----------
        dataset: Dataset
            Object of the dataset metadata
        run: Run
            Metadata of the run
        processed_data: ProcessedData
            Object containing the new processed data. md_uri is ignored and
            created automatically by this method

        Returns
        -------
        ProcessedData object with the metadata and the new created md_uri

        """
        self._omero_connect()
        try:
            # get the parent dataset 
            omero_dataset = self._conn.getObject('Dataset', dataset.id)

            # create an empty image
            numpy_image = [np.zeros((1,1))]
            def plane_gen():
                for p in numpy_image:
                    yield p

            omero_image = self.conn.createImageFromNumpySeq(plane_gen(), processed_data.name, 
                                                            1, 1, 1, 
                                                            description='',
                                                            dataset=omero_dataset) 
        finally:
            self._omero_close() 

        # set the attachment file
        processed_data.uuid = omero_image.id
        processed_data.md_uri = omero_image.id
        processed_data.uri = omero_image.id
        processed_data.run = run
        self.update_processed_data(processed_data)

        return processed_data    
