

class JobInput:
    """Container for a job input

    A job input is all the information needed to select the input data files of a job in an
    experiment

    Attributes
    ----------
    name: str
        Name of the input (ex -i)
    dataset: str
        Name of the dataset containing the inputs (ex 'data')
    query: str
        Query used to select images in the dataset (ex 'name=image.tif')
    origin_output_name: str
        Name of the output in the parent run if run on a processed dataset

    """
    def __init__(self, name: str = '', dataset: str = '',
                 query: str = '', origin_output_name: str = ''):
        self.name = name
        self.dataset = dataset
        self.query = query
        self.origin_output_name = origin_output_name


class JobInputs:
    """Container for multiple inputs of a job

    Attributes
    ----------
    inputs: list
        List of all the job inputs

    """
    def __init__(self):
        self.inputs = []

    def add_input(self, name, dataset, query, origin_output_name = ''):
        """Add a job input

        Parameters
        ----------
        name: str
            Name of the input (ex -i)
        dataset: str
            Name of the dataset containing the inputs (ex 'data')
        query: str
            Query used to select images in the dataset (ex 'name=image.tif')
        origin_output_name: str
            Name of the output in the parent run if run on a processed dataset

        """
        self.inputs.append(JobInput(name, dataset, query, origin_output_name))

    def add_job_input(self, job_input):
        """Add a job input

        Parameters
        ----------
        job_input: JobInput
            input to be added

        """
        self.inputs.append(job_input)


class Job:
    """Container for a job information

    A job information lists all the needed information to run a tool on an experiment

    Attributes
    ----------
    experiment: Experiment
        Container of the experiment to process
    tool: Tool
        Tool to run
    parameters: dict
        Set of parameters that setup the tool.
    inputs: JobInputs
        Description of the job inputs in the database

    """
    def __init__(self, experiment, tool, parameters, inputs):
        self.experiment = experiment
        self.tool = tool
        self.parameters = parameters
        self.inputs = inputs
