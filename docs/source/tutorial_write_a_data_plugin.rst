Tutorial: write a data plugin
=============================

In this tutorial we describe step by step how to implement a plugin to manage data with **bioimageit_core**. By default 
the **bioimageit_core** library has one data plugin: 

* LOCAL: a data manager based on local file system. Each experiment is a local directory and each data metadata are stored using *JSON* files.

Data plugins must contains 3 things:
1. ``plugin_info``: a dictionnary that contains the metadata of the plugin
2. ``ServiceBuilder``: a class that allows to instantiate the plugin service
3. ``DataService``: a class that implement the plugin service interface

A plugin should be stored in an independent Git reposotory with a name starting with ``bioimageit_`` to be findable by the BioImageIT plugin engine. As a example, we can refer 
to the repository of the `bioimageit-omero <https://github.com/bioimageit/bioimageit-omero>`_ plugin


Plugin info
-----------

A BioImageIT data plugin must contain a dictonnary called ``plugin_info`` with the plugin metadata. A BioImageIT plugin has 3 metadata:
1. The plugin name
2. The plugin type. The type shoud be `data` for a data plugin, `runner` for a runner plugin or `tools` for a tools manager plugin. 
3. The name of the plugin service builder

.. code-block:: python

    plugin_info = {
        'name': 'OMERO',
        'type': 'data',
        'builder': 'OmeroMetadataServiceBuilder'
    }


Data service builder
--------------------

The service builder is a class that allows to instantiate and initialize a single instance of the data plugin. The code bellow shows an
example of data service for the ``LocalServiceBuilder``

.. code-block:: python

    class LocalMetadataServiceBuilder:
        """Service builder for the metadata service"""

        def __init__(self):
            self._instance = None

        def __call__(self, **_ignored):
            if not self._instance:
                self._instance = LocalMetadataService()
            return self._instance

The constructor initialize a null instance of the ``LocalMetadataService``, and the ``__call__`` method instante a new
``LocalMetadataService``. Thus, when the ``LocalMetadataServiceBuilder`` is called it is always the same instance of the 
``LocalMetadataService`` that is used.             


Data service
------------

The data service is the class that implements the data management functionalities. Each method of the data service 
class is dedicated to a single data manipulation. The code below shows the list of the methods to implement where the 
comments indicate the inputs and outputs of the method.
 
.. code-block:: python

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


.. code-block:: python

    def get_workspace_experiments(self, workspace_uri):
        """Read the experiments in the user workspace

        Parameters
        ----------
        workspace_uri: str
            URI of the workspace

        Returns
        -------
        list of experiment containers  
          
        """


.. code-block:: python

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

.. code-block:: python

    def update_experiment(self, experiment):
        """Write an experiment to the database

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata

        """

.. code-block:: python

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

.. code-block:: python

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

.. code-block:: python

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

.. code-block:: python

    def update_raw_data(self, raw_data):
        """Read a raw data from the database

        Parameters
        ----------
        raw_data: RawData
            Container with the raw data metadata

        """ 

.. code-block:: python

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

.. code-block:: python

    def update_processed_data(self, processed_data):
        """Read a processed data from the database

        Parameters
        ----------
        processed_data: ProcessedData
            Container with the processed data metadata

        """

.. code-block:: python

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

.. code-block:: python

    def update_dataset(self, dataset):
        """Read a processed data from the database

        Parameters
        ----------
        dataset: Dataset
            Container with the dataset metadata

        """

.. code-block:: python

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

.. code-block:: python

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

.. code-block:: python

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

.. code-block:: python

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


Register the service
--------------------

The last step is to register the metadata service to the **bioimageit_core** data services factory. Open the file 
``bioimageit_core/plugins/data_factory.py``, and add a line at the end to register the service:

.. code-block:: python

    metadataServices.register_builder('LOCAL', LocalMetadataServiceBuilder())

In the example above, the string ``'LOCAL'`` is the name of the metadata service. Then, if we want to use this service, we need to specify it 
in the config file:

.. code-block:: javascript

    ...
    "metadata": {
        "service": "LOCAL",
    ...

Summary
-------

To summarize, in order to create a new metadata plugin we need to follow these steps:

* create a python file in ``bioimageit_core/plugins/``
* implement a ``DataServiceBuilder`` class.
* implement a ``MetadataService`` class.
* register the service at ``bioimageit_core/plugins/data_factory.py``
* setup the config.json file with the new plugin to be able to use it
