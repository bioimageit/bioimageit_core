Introduction
============

BioImageIT_core is a tool to facilitate interoperability between image processing software and datasets.
Datasets can be stored as json files or on an Omero database for example.
Wrapped image processing tools are called either locally or using containers
(Docker, Singularity).

Context
-------
BioImageIT_core has been developped by **Sylvain Prigent** in a project funded by `France-BioImaging <https://france-bioimaging.org/>`_.
BioImageIT_core is just the python API of the project. Please find all the other developped tools `here <https://gitlab.inria.fr/bioimage-it/>`_.

What BioImageIT_core is
------------------
BioImageIT_core is a python3 library the provide a python API to facilitate writing data processing scripts, wrapping data 
analysis tools from any language and ease comunication with an experiment database.
