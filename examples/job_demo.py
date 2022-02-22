import bioimageit_core.api as iit
from bioimageit_core.containers.runners_containers import Job

# First we connect to the database (here it is a local database)
req = iit.Request('./config_sample.json')
req.connect()

experiment = req.get_experiment('myexperiment/experiment.md.json')
## then we need an annotated experiment
#experiment = req.create_experiment(name='myexperiment',
#                                   author='sprigent',
#                                   date='now',
#                                   destination="./")
#req.import_dir(experiment=experiment,
#               dir_uri='./tests/test_images/data',
#               filter_=r'\.tif$',
#               author='sprigent',
#               format_='imagetiff',
#               date='now')
#req.annotate_from_name(experiment, 'Population', ['population1', 'population2'])
#req.annotate_using_separator(experiment, 'ID', '_', 1)
#req.display_experiment(experiment)

# we create the job
job = Job()
job.set_experiment(experiment)
job.set_tool(req.get_tool('spitfiredeconv2d_v0.1.2'))
job.set_input(name='i', dataset='data', query='')
job.set_param('sigma', '4')
job.set_param('regularization', '12')
job.set_param('weighting', '0.1')
job.set_param('method', 'SV')
job.set_param('padding', 'True')
job.set_output_dataset_name('deconv')

# run the job
req.run(job)
