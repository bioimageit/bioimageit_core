# -*- coding: utf-8 -*-
"""Omero module.

This module contains functions to import and export datasets
with Omero 

Example
-------
    Here is an example of how to import data:
    >>> from bioimagepy.omero import Omero
    >>> from bioimagepy.experiment import Experiment
    >>> ConfigAccess('../config.json')
    >>> myexperiment = Experiment('/path/to/experiment.md.json')
    >>> omero = Omero('demo.openmicroscopy.org', 4064, 'SylvainPrigent', 'password')
    >>> omero.add_observer(ProgressObserver()) # if you need to see import progress
    >>> omero.import_image(myexperiment, 123346) # to import a single image
    >>> omero.import_dataset(myexperiment, 4344) # to import a dataset
    >>> omero.close()

"""

import os
import numpy as numpy
from libtiff import TIFF

import omero
from omero.gateway import BlitzGateway, ImageWrapper

from bioimagepy.core.utils import Observable
from bioimagepy.experiment import Experiment


class Omero(Observable):
    """Run a process for a pipeline

    Run a process from data in an Experiment and save the
    results in new ProcessedDataset in the experiment

    Parameters
    ----------
    host
        Adresse of the Omero server
    port
        Port used to communicate with the server
    username
        Username to authenticate to the database
    password
        User password

    """

    def __init__(self, host: str, port: int, username: str, password: str):
        Observable.__init__(self)
        self.conn = None
        self._host = host
        self._connect(host, port, username, password)

    def close(self):
        self.conn.close()

    def _connect(self, host: str, port: int, username: str, password: str):

        # with BlitzGateway(username, password, host=host, port=port, secure=True) as conn:
        #    for p in conn.getObjects('Project'):
        #        print(p.name)

        self.conn = BlitzGateway(username, password, host=host, port=port, secure=True)
        rv = self.conn.connect()
        if not rv:
            print("Unable to connect to the Omero database")
        else:
            user = self.conn.getUser()
            print("Current user:")
            print("   ID:", user.getId())
            print("   Username:", user.getName())
            print("   Full Name:", user.getFullName())

    def import_dataset(self, experiment: Experiment, omero_dataset_id: int):
        dataset = self.conn.getObject("Dataset", omero_dataset_id)

        image_count = dataset.countChildren()

        k = 0
        for image in dataset.listChildren():
            k += 1
            self.notify_observers(
                100 * k / image_count, 'import image ' + str(k) + '/' + str(image_count)
            )
            self._import_image(experiment, image)

        self.notify_observers(100, 'Done')

    def import_image(self, experiment: Experiment, omero_image_id: int):
        image = self.conn.getObject("Image", omero_image_id)
        self._import_image(experiment, image)

    def _import_image(self, experiment: Experiment, image):

        # read metadata from omero
        rawdatasetdir = os.path.dirname(experiment.md_uri)
        filename = os.path.join(rawdatasetdir, 'data', image.getName())
        author = image.getAuthor()
        date = image.getDate().strftime('%Y-%m-%d %I:%M %S %p')
        extension = os.path.splitext(image.getName())[1][1:]

        tags = dict()
        for ann in image.listAnnotations():
            if ann.OMERO_TYPE == omero.model.MapAnnotationI:
                for kv in ann.getValue():
                    tags[kv[0]] = kv[1]

        # print('readed tags:')
        # print('\t author:', author)
        # print('\t date:', date)
        # print('\t extension:', extension)
        # print('\t tags:', tags)

        # write metadata to the experiment
        experiment.import_data(
            filename,
            image.getName(),
            author=author,
            format=extension,
            date=date,
            tags=tags,
            copy=False,
        )

        # register tag to experiment if not exists
        for tag in tags:
            experiment.set_tag(tag, False)

        # copy image
        channel = 0
        imageData = self._get_data(image, channel)
        tif = TIFF.open(filename, mode='w')
        for t in range(imageData.shape[0]):
            for z in range(imageData.shape[1]):
                tif.write_image(imageData[t, z, :, :])
        tif.close()

    def _get_data(self, img, c=0):
        """
        Get 4D numpy array of pixel data, shape = (size_t, size_z, size_y, size_x)
        :param  img:        omero.gateway.ImageWrapper
        :c      int:        Channel index
        """
        size_z = img.getSizeZ()
        size_t = img.getSizeT()
        # get all planes we need in a single generator
        zct_list = [(z, c, t) for t in range(size_t) for z in range(size_z)]
        pixels = img.getPrimaryPixels()
        plane_gen = pixels.getPlanes(zct_list)

        t_stacks = []
        for t in range(size_t):
            z_stack = []
            for z in range(size_z):
                # print("plane c:%s, t:%s, z:%s" % (c, t, z))
                z_stack.append(next(plane_gen))
            t_stacks.append(numpy.array(z_stack))
        return numpy.array(t_stacks)
