Tutorial: wrap a tool
=====================

In this tutorial, we details the standardized architecture for a tool package. This architecture facilitate 
tools access and sharing. 

A package can contain one or several wrappers. The package architecture is as follows:

* ``.shed.yml``: a file describing the tools (authors, toolboxes names...)
* ``test-data``: a directory containing data for demo and functional testing
* ``wrapper.xml``: One or several wrapper file. One wrapper per tool

This organisation is the same as the one used in the Galaxy Project for BioImageIT to be fully compatible with Galaxy Project

Shed file
---------

The shed file descibe the tool origin and how BioImageIT will classify it in the toolboxes tree. Bellow an example file 
gives the ``.shed.yml`` file content:

.. code-block:: yaml

  categories: 
    - Denoising
    - Filtering
  description: 2D image smooth with mean filtering  
  homepage_url: https://gitlab.inria.fr/bioimage-it/sampletool/
  long_description: 2D image smooth with mean filtering 
  name: SampleTool
  owner: sylvainprigent

The `categories` entry is a list of the toolboxes where the tool(s) will appear.
The `description` and `long_description` are short and long description to identify what is the tool(s) purpose. These descriptions are
displayed to the user when browsing the toolboxes.
The `homepage_url` is a web URL of the original tool. Idealy this should be a GitHub or GitLab public page.
Finally `name` and `owner` are the names of the tool and the author(s) to identify them. 

Wrapper
-------

The tool wrapper is an `XML` file describing how to run the tool. An example is shown bellow for a 2D image Wiener deconvolution. It is a classical Galaxy Project wrapper. 
The command is ``simgwiener2d`` and take 5 arguments, the input image ``-i``, the output image ``-o``, and 3 parameters ``-sigma``, ``-lambda`` 
and ``-padding``. 
The first section is the `<requirements>`. It contains the description of the method to install the tool and its dependencies.
The section `<command>` gives the command line that is executed when the tool is ran. Note that all the values are replaced 
with variables like ``${sigma}`` for the input ``-sigma``. These variables will be replaced with the user inputs at run time.
In order to describe the tool inputs and outputs, the wrapper presents two specefic section: `<inputs>` and `<outputs>`. 
Each input of the tool must be descibed in a `<param>` subsection and each output in a `<data>` subsection.     

The `<test>` section is important to automatically test that the wrapper and the tools are working correctly. This section 
can contains several tests and each test is the list of the input and output parameters and data values.

The `<help>` section should contains the link to a html or web documentation. The documentation can be stored locally in the 
wrapper directory in a *doc* folder. This section can be completed with the `<citations>` one with references. 


.. code-block:: xml

    <tool id="wienerdeconv2d" name="Wiener 2D" version="0.1.2" python_template_version="3.5">
        <requirements>
            <package type="conda" env="simglib">-c sylvainprigent simglib=0.1.2 python=3.9</package>
        </requirements>
        <command detect_errors="exit_code"><![CDATA[
            simgwiener2d -i ${i} -o ${o} -sigma ${sigma} -lambda ${lambda} -padding ${padding}
        ]]></command>
        <inputs>
            <param type="data" name="i" format="imagetiff" label="Input Image" help="2D image" />
            <param argument="-sigma" type="float" value="1.5" label="Sigma" help="Gaussian PSF width" />
            <param argument="-lambda" type="float" value="0.01" label="Lambda" help="Regularization parameter" />
            <param argument="-padding" type="select" label="Padding" help="Add a padding to process pixels in borders" optional="true">
                <option value="false">False</option>
                <option value="true">True</option>
            </param>
        </inputs>
        <outputs>
            <data name="o" format="imagetiff" label="Denoised image" />
        </outputs>
        <tests>
            <test>
                <param name="i" value="image.tif" />
                <param name="sigma" value="1.5" />
                <param name="lambda" value="0.001" />
                <param name="padding" value="true" />
                <output name="o" file="image_o.tif" compare="sim_size" />
            </test>
        </tests>
        <help><![CDATA[
            https://github.com/sylvainprigent/simglib
        ]]></help>
        <citations>
        </citations>
    </tool>


Packaging and dependencies
--------------------------

BioImageIT is able to run tool that are packaged either using **Conda** or **Docker**. 

When using conda, the authors need to create a conda package and store it in anaconda.org. Then, the `<requirements>` section looks like the folowing:

.. code-block:: xml

    <requirements>
        <package type="conda" env="simglib">-c sylvainprigent simglib=0.1.2 python=3.9</package>
    </requirements>

The package needs 2 arguments: type and env. For a **Conda** package the type is *conda* and the environement is the name
of the environement that will be created to install the tool. In the example above we named it `simglib` since it is the 
name of the library that we install for the tool. Finally, the main body of `<package>` is the ``conda install`` arguments.
In the example we wrote ``-c sylvainprigent simglib=0.1.2 python=3.9`` to create an environement with python 3.9 and install
the version 0.1.2 of simglib from the *sylvainprigent* conda channel.

When using Docker, the author needs to build a docker image and store it in Docker hub or a Gitlab register. Then, 
the requirement `<requirements>` section is:

.. code-block:: xml
    
    <requirements>
        <container type="docker">registry.gitlab.inria.fr/bioimage-it/sampletool:766efe8b8397fef0115e20f8e7cd2853a0e0e0d5</container>
    </requirements>

where the container type is docker and the container body is the adress of the docker image. 


.. note::
    There is no special section in the wrapper to specify a repository of the source code, but for transparency, it is 
    recommended to add is in the tool documentation.


Summary
-------

In this tutorial, we show with an example how to create a tool package compatible with *BioImageIT* and Galaxy Project. This has 
the advantages of using the original source code without changing it, but just packaging it with *Docker* or *Conda* and discribing it with a *wrapper* XML file. 
To make a tool available, please send a push request `here <https://github.com/bioimageit/bioimageit-tools>`.
