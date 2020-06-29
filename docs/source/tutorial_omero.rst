Tutorial: Omero
===============

In this tutorial, we show how to import images from Omero 

`Omero <https://www.openmicroscopy.org/>`_ is an image database dedicated to biological images. This database can only handle biological
images, but no other data format. This is the reason why we do not defelop a metadata plugin but a dedicated module to allow images and dataset 
import from `Omero <https://www.openmicroscopy.org/>`_ to a BioImageIT experiment.


Import
------

To import a single image from `Omero <https://www.openmicroscopy.org/>`_, we can use the Omero module as follows.

.. code-block:: python

  from bioimagepy.config import ConfigAccess
  from bioimagepy.omero import Omero
  from bioimagepy.experiment import Experiment
 
  # init bioimagepy settings
  ConfigAccess('../config.json')

  # load the experiment
  myexperiment = Experiment('/path/to/the/experiment.md.json')

  # connect to Omero and import the image
  omero = Omero('demo.openmicroscopy.org', 4064, 'YourOmeroUsername', 'YourOmeroPassWord')
  omero.import_image(myexperiment, 123346)
  omero.close()

The script above will import a single image to the raw dataset of the experiment. The `import_image` method import the image content 
and the image metadata (including map tags).

To import a full dataset from `Omero <https://www.openmicroscopy.org/>`_, we can use the Omero module as follows.

.. code-block:: python

  from bioimagepy.config import ConfigAccess
  from bioimagepy.omero import Omero
  from bioimagepy.experiment import Experiment
 
  # init bioimagepy settings
  ConfigAccess('../config.json')

  # load the experiment
  myexperiment = Experiment('/path/to/the/experiment.md.json')

  # connect to Omero and import the image
  omero = Omero('demo.openmicroscopy.org', 4064, 'YourOmeroUsername', 'YourOmeroPassWord')
  omero.import_dataset(myexperiment, 3291)
  omero.close()

The script above will import a all the image from the selected dataset in Omero to the raw dataset of the experiment. The `import_dataset` method import the images content 
and their metadata (including map tags).
