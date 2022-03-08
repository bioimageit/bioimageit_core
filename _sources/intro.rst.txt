Introduction
============

`bioimageit_core`` is a tool to facilitate interoperability between image processing software and datasets.
Datasets can be stored as json files or on an Omero database for example.
Wrapped image processing tools are called either locally (Conda) or using containers
(Docker, Singularity).

Context
-------
``bioimageit_core`` has been developed by **Sylvain Prigent** in a project funded by `France-BioImaging <https://france-bioimaging.org/>`_.
``bioimageit_core`` is just the python API of the project. Please find all the other developed tools `here <https://github.com/bioimageit/>`_.

What bioimageit_core is
-----------------------
`bioimageit_core` is a python3 library the provide a python API to facilitate writing data processing scripts, wrapping data 
analysis tools from any language and ease communication with an experiment database.
