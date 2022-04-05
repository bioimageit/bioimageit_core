

class PipelineInput:
    def __init__(self, name='', dataset='', query='', origin_output_name=''):
        self.name = name 
        self.dataset = dataset
        self.query = query
        self.origin_output_name = origin_output_name


class PipelineOutput:
    def __init__(self, name='', save=True ):
        self.name = name
        self.save = save
    

class PipelineParameter:
    def __init__(self, name='', value=''):
        self.name = name
        self.value = value       


class PipelineStep:
    def __init__(self):
        self.name = ''
        self.tool = ''
        self.inputs = [] # PipelineInput
        self.parameters = [] # PipelineParameter
        self.outputs = [] # PipelineOuputs
        self.output_dataset_name = ''
        self.already_ran = False

    def add_input(self, input: PipelineInput):
        self.inputs.append(input)

    def add_ouptut(self, output: PipelineOutput):
        self.outputs.append(output)    

    def add_parameter(self, parameter: PipelineParameter):
        self.parameters.append(parameter)


class Pipeline:
    def __init__(self):
        self.type = 'pipeline'
        self.name = ''
        self.description = ''
        self.user = ''
        self.date = ''
        self.uuid = ''
        self.bioimageit_version = ''
        self.steps = []

    def add_step(self ):
        pass    
