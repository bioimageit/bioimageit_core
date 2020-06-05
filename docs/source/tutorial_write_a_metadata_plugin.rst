Tutorial: write a metadata plugin
=================================

In this tutorial we describe step by step how to implement a plugin to manage metadata for **BioImagePy**. By default 
the **BioImagePy** library has one metadata plugin: 

* LOCAL: a metadata manager based on local file system. Each experiment is a local directory and each data metadata are stored using *JSON* files.

Metadata plugins are implemented using the service design pattern. To make it easier to identify the services plugins in the 
python code repository we prefix the python plugin file with ``service_``. 
Thus, to create a new metadata plugin you need to create a python file at ``bioimagepy/metadata/service_yourservicename.py``

Then, all the code will be in this single file. A metadata service plugin file contains two classes: the ``ServiceBuilder`` and 
the ``MetadataService``

Metadata service builder
------------------------

The service builder is a class that allows to instantiate and initialize a single MetadataService. The code bellow shows an
example of metadata service for the ``LocalServiceBuilder``

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
``MetadataService`` that is used.             

Metadata service
----------------

The metadata service is the class that implements the metadata management functionalities. Each method of the metadata service 
class is dedicated to a single metadata manipulation. The code below shows the list of the methods to implement where the 
comments indicate the inputs and outputs of the method.
 
.. code-block:: python

    def read_rawdata(self, md_uri: str) -> RawDataContainer:
        """Read a raw data metadata from the database

        Parameters
        ----------
        md_uri
            URI of the data

        Returns
        -------
        a RawDataContainer that stores the raw data metadata 
                
        """

.. code-block:: python

    def write_rawdata(self, container: RawDataContainer, md_uri: str)
        """Write a raw data metadata to the database

        Parameters
        ----------
        container
            object that contains the raw data metadata to write
        md_uri
            URI of the data
                
        """

.. code-block:: python

    def read_processeddata(self, md_uri: str) -> ProcessedDataContainer:
        """Read a processed data metadata from the database

        Parameters
        ----------
        md_uri
            URI of the data
                
        Returns
        -------
        ProcessedDataContainer: object that contains the readed processed data metadata    

        """

.. code-block:: python

    def write_processeddata(self, container: ProcessedDataContainer, md_uri: str): 
        """Write a processed data metadata to the database

        Parameters
        ----------
        container
            object that contains the processed data metadata to write
        md_uri
            URI of the data
                
        """ 

.. code-block:: python

    def read_rawdataset(self, md_uri: str) -> DataSetContainer:
        """Read a raw dataset metadata from the database

        Parameters
        ----------
        md_uri
            URI of the dataset
                
        Returns
        -------
        DataSetContainer: object that contains the readed dataset metadata    

        """

.. code-block:: python

    def write_rawdataset(self, container: DataSetContainer, md_uri: str): 
        """Write a raw dataset metadata to the database

        Parameters
        ----------
        container
            object that contains the raw dataset metadata to write
        md_uri
            URI of the dataset
                
        """ 

.. code-block:: python

    def read_processeddataset(self, md_uri: str) -> DataSetContainer:
        """Read a processed dataset metadata from the database

        Parameters
        ----------
        md_uri
            URI of the dataset
                
        Returns
        -------
        DataSetContainer: object that contains the readed dataset metadata    

        """

.. code-block:: python

    def write_processeddataset(self, container: DataSetContainer, md_uri: str): 
        """Write a processed dataset metadata to the database

        Parameters
        ----------
        container
            object that contains the processed dataset metadata to write

        md_uri
            URI of the dataset
                
        """    

.. code-block:: python

    def add_run_processeddataset(self, run:RunContainer, dataset_md_uri:str):
        """Add a run to a processed dataset

        Parameters
        ----------
        run
            Container of the Run metadata
        dataset_md_uri
            URI of the ProcessedDataset     

        """

.. code-block:: python

    def create_processed_dataset(self, name: str, experiment_md_uri: str):
        """create a new processed dataset

        Parameters
        ----------
        name
            Name of the processed dataset
        experiment_md_uri
            URI of the experiment that contains the dataset    

        """

.. code-block:: python

    def create_data_processeddataset(self, data: ProcessedDataContainer, md_uri: str): 
        """create a new data metadata in the dataset
        
        The input data object must contain only the metadata (ie no
        uri and no md_uri). 
        This method generate the uri and the md_uri and save all the
        metadata

        Parameters
        ----------
        data
            metadata of the processed data to create 
        md_uri
            URI of the processed dataset    
        
        """      

.. code-block:: python

    def read_experiment(self, md_uri: str) -> ExperimentContainer:  
        """Read an experiment metadata
        
        Parameters
        ----------
        md_uri
            URI of the experiment in the database

        Returns
        -------    
        ExperimentContainer: object that contains an experiment metadata    
         
        """   

.. code-block:: python

    def write_experiment(self, container: ExperimentContainer, md_uri:str):
         """Write an experiment metadata to the database
        
        Parameters
        ----------
        container 
            Object that contains an experiment metadata  
        md_uri
            URI of the experiment in the database 

        """ 

.. code-block:: python

    def create_experiment(self, container: ExperimentContainer, uri: str):
        """Create a new experiment metadata to the database
        
        Parameters
        ----------
        container 
            Object that contains an experiment metadata  
        uri
            URI of the experiment in the database 

        """ 

.. code-block:: python

    def import_data(self, data_path:str, rawdataset_uri: str, metadata: RawDataContainer, copy: bool):
        """Import a data to a raw dataset

        Parameters
        ----------
        data_path
            local path of the data to import
        rawdataset_uri
            URI of the raw dataset where the data will be imported
        metadata
            Metadata of the data to import
        copy
            True if the data is copied to the Experiment database
            False otherwise            

        """

.. code-block:: python

    def read_run(self, md_uri: str) -> RunContainer:
        """Read a run metadata from the data base

        Parameters
        ----------
        md_uri
            URI of the run entry in the database   

        Returns
        -------
        RunContainer: object contining the run metadata            

        """

.. code-block:: python

    def write_run(self, container: RunContainer, md_uri: str):
        """Write a run metadata to the data base

        Parameters
        ----------
        container
            Object contining the run metadata 
        md_uri
            URI of the run entry in the database              

        """

.. code-block:: python

    def query_rep(self, repository_uri: str, filter: str) -> list:
        """Query files in a repository

        Parameters
        ----------
        repository_uri
            URI of the repository
        filter  
            Regular expression to select a subset of file base on their names 

        Returns
        -------
        The list of selected files    

        """

.. code-block:: python

    def create_output_uri(self, output_rep_uri: str, output_name: str, format: str, corresponding_input_uri:str) ->str:
        """Create the URI of an run output data file

        Parameters
        ----------
        output_rep_uri
            Output directory of the run
        output_name
            Output filename 
        format
            Output file format 
        corresponding_input_uri
            URI of the origin input data 

        Returns
        -------
        the created URI           

        """

Register the service
--------------------

The last step is to register the metadata service to the **BioImagePy** metadata services factory. Open the file 
``bioimagepy/metadata/factory.py``, and add 
a line at the end to register the service:

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

* create a python file in ``bioimagepy/metadata/``
* implement a ``MetadataServiceBuilder`` class.
* implement a ``MetadataService`` class.
* register the runner at ``bioimagepy/metadata/factory.py``
* setup the config.json file with the new builder to be able to use it
