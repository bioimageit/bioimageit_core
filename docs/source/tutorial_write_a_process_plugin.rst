Tutorial: write a runner plugin
===============================

In this tutorial we describe step by step how to implement a process ``Runner`` for **BioImagePy**. By default 
the **BioImagePy** library has two runners: 

* LOCAL: a runner that execute process localy. This means that the binaries of the process have to be installed localy.
* SINGULARITY: a runner that execute a process from a Docker image using the Singularity software.

Runners are implemented using the service design pattern. To make it easier to identify the services plugins in the 
python code repository we prefix the python plugin file with ``service_``. 
Thus, to create a new ``Runner`` you need to create a python file at ``bioimagepy/runners/service_yourservicename.py``

Then, all the code will be in this single file. A runner service plugin file contains two classes: the ``ServiceBuilder`` and 
the ``RunnerService``

Runner service builder
----------------------

The service builder is a class that allows to instantiate and initialize a single RunnerService. The code bellow shows an
example of runner service for the ``LocalServiceBuilder``

.. code-block:: python

    class LocalRunnerServiceBuilder:
        """Service builder for the runner service"""
        def __init__(self):
            self._instance = None

        def __call__(self, **_ignored):
            if not self._instance:
                self._instance = LocalRunnerService()
            return self._instance

The constructor initialize a null instance of the ``LocalRunnerService``, and the ``__call__`` method instante a new
``LocalRunnerService``. Thus, when the ``LocalRunnerServiceBuilder`` is called it is always the same instance of the 
``RunnerService`` that is used.             

Runner service
--------------

The runner service is the class that implements the runner functionalities. The code bellow shows the implementation of 
the ``LocalRunnerService``. As we can see, a runner service has a single method called ``exec``. This method has two inputs: the ``ProcessContainer``
which is a class that contains all the metadata of the ``Process``, and ``args`` the list of the command line arguments. For the 
example of local runner, we just call the command line arguments with subprocess. Another example of runner service implementation can 
be found at ``bioimagepy/runners/service_singularity.py`` 

.. code-block:: python

    class LocalRunnerService:
        """Service for local runner exec
        
        To initialize the database, you need to set the xml_dirs from 
        the configuration and then call initialize
        
        """
        def __init__(self):
            self.service_name = 'LocalRunnerService'

        def exec(self, process:ProcessContainer, args):
            """Execute a process

            Parameters
            ----------
            process
                Metadata of the process
            args
                list of arguments    

            """
            subprocess.run(args)

Register the runner
-------------------

The last step is to register the runner to the **BioImagePy** runner factory. Open the file ``bioimagepy/runners/factory.py``, and add 
a line at the end to register the runner:

.. code-block:: python

    runnerServices.register_builder('LOCAL', LocalRunnerServiceBuilder())

In the example above, the string ``'LOCAL'`` is the name of the runner. Then, if we want to use this runner, we need to specify it 
in the config file:

.. code-block:: javascript

    ...
    "process": {
        "service": "LOCAL",
    ...

Summary
-------

To summarize, in order to create a new ``Runner`` we need to follow these steps:

* create a python file in ``bioimagepy/runner/``
* implement a ``RunnerServiceBuilder`` class.
* implement a ``RunnerService`` class.
* register the runner at ``bioimagepy/runners/factory.py``
* setup the config.json file with the new builder to be able to use it
