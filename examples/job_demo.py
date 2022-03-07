import os
import shutil
import bioimageit_core.api as iit
from bioimageit_core.containers.runners_containers import Job

# First we connect to the database (here it is a local database)
req = iit.Request('../config.json')
req.connect()

#if os.path.isdir('./myexperiment/'):
#    shutil.rmtree('./myexperiment/')

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

## we create the job
#job = Job()
#job.set_experiment(experiment)
#job.set_tool(req.get_tool('spitfiredeconv2d_v0.1.2'))
#job.set_input(name='i', dataset='data', query='')
#job.set_param('sigma', '4')
#job.set_param('regularization', '12')
#job.set_param('weighting', '0.1')
#job.set_param('method', 'SV')
#job.set_param('padding', 'True')
#job.set_output_dataset_name('deconv')

## run the job
#experiment = req.run(job)

## query one of the data
#processed_data = req.query(experiment, 'deconv', 'Population=population1 AND ID=001')[0]
#origin = req.get_origin(processed_data)
#print('processed_data=', processed_data.uri)
#print('processed_data=', origin.uri)


## threshold particles
#threshold_particles = req.get_tool('threshold_particles_v1.0.0')
#threshold_particles.man()

#job2 = Job()
#job2.set_experiment(experiment)
#job2.set_tool(threshold_particles)
#job2.set_input(name='input', dataset='deconv', query='')
#job2.set_param('threshold', 'Minimum')
#job2.set_output_dataset_name('particles')

#experiment = req.run(job2)


#processed_data = req.query(experiment, 'particles', 'Population=population1 AND ID=001', 'draw')
#print(processed_data[0].uri)

#wilcoxon_tool = req.get_tool('Wilcoxon_v1.0.0')
#wilcoxon_tool.man()

#job3 = Job()
#job3.set_experiment(experiment)
#job3.set_tool(wilcoxon_tool)
#job3.set_input(name='x', dataset='particles', query='Population=population1', origin_output_name='count')
#job3.set_input(name='y', dataset='particles', query='Population=population2', origin_output_name='count')
#job3.set_output_dataset_name('wilcoxon')

#experiment = req.run(job3)

experiment = req.get_experiment('./myexperiment/experiment.md.json')
wilcoxon_data = req.query(experiment, 'wilcoxon', 'name=p')[0]
print('processed data = ', wilcoxon_data.name )

with open(wilcoxon_data.uri, 'r') as content_file:
    p = content_file.read()
print('p-value=', p)