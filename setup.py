import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bioimagepy",
    version="0.0.1",
    author="Sylvain Prigent",
    author_email="sylvain.prigent@inria.fr",
    description="write biological data processing pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.inria.fr/bioimage-it/bioimagepy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "PrettyTable>=1.0.1",
        "pyyaml>=5.3.1",
        "wget>=3.2",
        "spython>=0.0.85",
        "allgo>=0.1.11",
        "omero-py>=5.8.3"
    ],
)
