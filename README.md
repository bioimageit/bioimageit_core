
# BioImageIT core

BioImageIT core is a python library to write biological data analysis pipelines.

# Documentation

The documentation is available [here](https://bioimage-it.gitlabpages.inria.fr/bioimagepy/).

# Development

## Run tests

Test are written with unittest python package. All tests are located in the subpackage bioimagepy/tests.
Run tests with the command:

```bash
cd bioimageit_core
pipenv run python -m unittest discover -v
```

## Build the documentation

The documentation is written with Sphinx. To build is run the commands:

```bash
cd docs
pipenv run sphinx-build -b html ./source ./build
```

## Generate the requirements.txt

The `requirements.txt` file is generated from Pipenv with:

```bash
pipenv lock --requirements > requirements.txt
```
