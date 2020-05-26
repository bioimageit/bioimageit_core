.. _guide:

Guide
=====

BioImagePy is a python3 library. It implements the concepts described in the BioImageIT recommendations. 
In the scheme below we can see the position of BioImagePy in the BioImageIT ecosystem. In fact BioImagePy is the 
API that connect low level image processing and data management to high level end users applications.

.. figure::  images/apps_layers.png
   :align:   center


For data management, BioImagePy implement a set of function to manage and annotate data at the Experiment 
scale. For image processing tools BioImagePy implements a set of functions to query a tool database and 
to run tools on data.  
For Data management and process management, BioImagePy define an API that can be implemented with plugins. For data 
management by default, data are managed in a JSON file system. If we want to use the BioImagePy API to manage data on 
a SQL database for example, we can implement a data management plugin that plug the BioImagePy API with the SQL database. 
For process run, BioImagePy by defaut run tools using Docker containers in the local machine. If we want to run processing
tool with a job sckeduler for example, we can write a process runner plugin that plug the BioImagePy API to the job sckeduler.

The advantage of this BioImagePy architecture it to enable writing high level python code to manage and annotate data and deploy it 
in different hardware or network architecture without need to update the high level code, but just the configuration file.


Data Management
---------------

In the BioImageIT recommendations, we propose to manage data using a three layer representation:

* **Experiment**: an experiment contains one dataset of raw data named "data" and a list of processed datasets. Each processed dataset corresponds to a run of a tool.
* **DataSet**: a dataset contains a list of data that can be raw or processed
* **Data**: a data contains a single data and the associated metadata. For a ``RawData`` metadata are a set of *key:values* tags specific to the experiment, and for ``ProcessedData``, metadata are the origin data and the process run information. 

In this section we show the main functions implemented in the BioImagePy library to handle ``Data``, ``Dataset`` and ``Experiment``. Please
refer to the docstring documentation to get more advanced features.
To create an experiment, *BioImagePy* have a dedicated function with the following syntax:

.. code-block:: python3

    myexperiment = Experiment()
    myexperiment.create('myexperiment', 'Sylvain Prigent', './')

This creates an empty repository with the basic metadata of the experiment. Then we can import a single data:

.. code-block:: python3

    myexperiment.import_data(uri='data_uri', name='mydata', author='Sylvain Prigent', dataformat='tif', createddata='now', copy_data=True)

or a multiple data from a directory:

.. code-block:: python3

    myexperiment.import_dir(dir_uri='./my/local/dir/', filter='\.tif$', author='Sylvain Prigent', format='tif', date='now', copy_data=True)

Then the next step is to tag the data. It can be done in batch with functions like:

.. code-block:: python3

    myexperiment.tag_from_name(tag='population', ['population1', 'population2'])

or:

.. code-block:: python3

    myexperiment.tag_using_seperator(tag='ID', separator='_', value_position=1)

that will create tags and tag the data by extracting information from the data file names. 
The first case will search the words *population1* and *population2* in the data file name and 
associate it to the tag *population* if on the the word *population1* or *population2* is found. 
The second case shows how to extract information from the data file name using separators. Here we 
extract the sub-string in the file name that is located between two *_* and after the first *_*, 
and associate the extracted value to the tag *ID*.
We can also manually tag one data by extracting it and manually adding a tag:

.. code-block:: python3

    data = myexperiment.get_data(dataset_name: 'data', query: 'name=population1_001.tif')
    data.set_tag("population", "Population1")
    data.set_tag("ID", "001")

The *BioImagePy* library also allows to access directly a ``DataSet``:

.. code-block:: python3

    raw_dataset = myexperiment.get_dataset(name: 'data')

and interact with the data in the ``DataSet``:

.. code-block:: python3

    data = raw_dataset.get_data(...)
    raw_dataset.add_data(...)

Process Running
---------------

The BioImageIT recommendation descibe a packaging method to package data processing tools using an XML file and a docker image. 
The *BioImagePy* library, implement functionalities to manipulate and run packaged tools using three level: Process, Runner and Pipeline.

A ``Process`` is a python class in *BioImagePy* that allows to identify a processing tool. It load the tool XML file and allows to print and access the process information. 

.. code-block:: python3

    myprocess = Process(url/of/the/process/wrapper.xml)
    myprocess.man()

In practice, we do not need to instantiate directly a ``Process`` since *BioImagePy* provides a ``ProcessAccess`` 
class that manage a process database. We can then access a ``Process`` simply using the tool name and version:

.. code-block:: python3 

    myprocess = ProcessAccess().get('sampletool_v0.0.1')
    myprocess.man()

The ``Runner`` class allows to run a process on data. This is the core class of the processing 
functionality of *BioImagePy*. Running a process can be done as follows:

.. code-block:: python3 

    myrunner = Runner(ProcessAccess().get('ndsafir_v1.0.0') 
    myrunner.exec('i', 'myimage.tif',
                  'patch', patch,               
                  'iter', iteration,
                  'o', 'denoised.tif') 


Finally the ``Pipeline`` class is a convenient class that allows to run a sequence of processes in data stored in an ``Experiment``:

.. code-block:: python3 

    mypipeline = Pipeline(Experiment('my/experiment/uri'))

    p1 = mypipeline.add_process('spartion2d_v1.0.0')
    p1.set_parameters('sigma', '3', 
                      'weighting', '0.1', 
                      'regularization', '2')
    p1.add_input('i', 'data', '')
    p1.set_dataset_name('deconv2d')

    p2 = mypipeline.add_process('particleanalyzer_v1.0.0')
    p2.set_parameters('threshold', 'Default dark')
    p2.add_input('i', 'deconv', '')
    p2.set_dataset_name('particles')

    mypipeline.run()


Further reading
---------------

In this short introduction guide we show the basic informations we need to use *BioImagePy*. For a more advanced use, we preconise 
reading the following tutorials.
