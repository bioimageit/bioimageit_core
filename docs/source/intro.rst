Introduction
============

BioImagePy is a tool to facilitates de interoperability between image processing software and datasets. 
Datasets can be stored in a json file system or on an Omero database for example. Wrapped image processing tools are wrapped and 
called either locally or using containers (Docker, Singularity)  

Context
-------
BioImagePy has been developped by **Sylvain Prigent** in a project funded by `France-BioImaging <https://france-bioimaging.org/>`_
BioImagePy is just the python API of the project. Please find all the other developped tools `here <https://gitlab.inria.fr/bioimage-it/>`_

What BioImagePy is
------------------
BioImagePy is a python3 library the provide a python API to facilitate writing data processing scripts, wrapping data 
analysis tools from any languages and ease to comunication with an experiment database.