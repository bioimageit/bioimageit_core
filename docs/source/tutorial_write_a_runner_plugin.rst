Tutorial: write a runner plugin
===============================

In this tutorial we describe step by step how to implement a tool ``Runner`` for **bioimageit_core**. By default 
the **bioimageit_core** library has two runners: 

* CONDA: a runner that execute process localy from conda environements. This means that the binaries of the process have to be installed locally with Conda.
* DOCKER: a runner that execute a process from a Docker image. It needs Docker client to be installed.

Runners are implemented using the service design pattern. To make it easier to identify the services plugins in the 
python code repository we prefix the python plugin file with ``runner_``. 
Thus, to create a new ``Runner`` you need to create a python file at
``bioimageit_core/plugins/runner_yourservicename.py``

Then, the main class of the runner is in this single file. A runner service plugin file contains two classes: the
``ServiceBuilder`` and
the ``RunnerService``

Runner service builder
----------------------

The service builder is a class that allows to instantiate and initialize a single runner service. The code bellow shows
an example of runner service for the ``LocalServiceBuilder``

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
the ``LocalRunnerService``. As we can see, a runner service has a 3 methodd called ``set_up``, ``exec`` and
``tear_down``. These methods have one common input: the ``Tool`` which is a class that contains all the
metadata of the tool. The exec method has one extra argument called ``args`` that is the list of the command line
arguments. For the example of local runner, we just call the command line arguments with subprocess. We do not need the
``set_up`` and the ``tear_down`` methods to initialize and clean the run environement. Another more
complex example of runner service implementation can be found at ``bioimageit_core/plugins/runner_docker.py``. For the
Docker case, the ``set_up`` method pull and run the Docker image, the ``exec`` method execute the command line in the
Docker container, and the ``tear_down`` method stops and removes the container.

.. code-block:: python

    class LocalRunnerService:
        """Service for local runner exec
        
        To initialize the database, you need to set the xml_dirs from 
        the configuration and then call initialize
        
        """
        def __init__(self):
            super().__init__()
            self.service_name = 'LocalRunnerService'

        def set_up(self, process: Tool):
            """setup the runner

            Add here the code to initialize the runner

            Parameters
            ----------
            process
                Metadata of the process

            """
            pass

        def exec(self, process:Tool, args):
            """Execute a process

            Parameters
            ----------
            process
                Metadata of the process
            args
                list of arguments    

            """
            subprocess.run(args)

        def tear_down(self, process: Tool):
            """tear down the runner

            Add here the code to down/clean the runner

            Parameters
            ----------
            process
                Metadata of the process

            """
            pass

Register the runner
-------------------

The last step is to register the runner to the **bioimageit_core** runner factory. Open the file
``bioimageit_core/plugins/runners_factory.py``, and add a line at the end to register the runner:

.. code-block:: python

    runnerServices.register_builder('LOCAL', LocalRunnerServiceBuilder())

In the example above, the string ``'LOCAL'`` is the name of the runner. Then, if we want to use this runner, we need to
specify it in the config file:

.. code-block:: javascript

    ...
    "process": {
        "service": "LOCAL",
    ...

Summary
-------

To summarize, in order to create a new ``Runner`` we need to follow these steps:

* create a python file in ``bioimageit_core/plugins/runner_name.py``
* implement a ``RunnerServiceBuilder`` class.
* implement a ``RunnerService`` class.
* register the runner at ``bioimageit_core/plugins/runners_factory.py``
* setup the config.json file with the new builder to be able to use it
