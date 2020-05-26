# BioImagePy

BioImagePy is a python library to write biological data analysis pipelines.
It runs command line application from local or

# Run tests

Test are written with unittest python package. All tests are located in the subpackage bioimagepy/tests.
Run tests with the command:
```bash
cd bioimagepy
python3 -m unittest discover -v
```

# Build the documentation

The documentation is written with Sphinx. To build is run the commands:
```bash
cd docs
mkdir build
sphinx-build -b html ./source ./build
```