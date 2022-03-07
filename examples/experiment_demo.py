import bioimageit_core.api as iit

# First we connect to the database (here it is a local database)
req = iit.Request('./config_sample.json')
req.connect()

# Create an experiment
experiment = req.create_experiment(name='myexperiment',
                                   author='sprigent',
                                   date='now',
                                   destination="./")

# Import a directory of data to the experiment
req.import_dir(experiment=experiment,
               dir_uri='./tests/test_images/data',
               filter_=r'\.tif$',
               author='sprigent',
               format_='imagetiff',
               date='now')

# Tag the images using the information in the file names
req.annotate_from_name(experiment, 'Population', ['population1', 'population2'])
req.annotate_using_separator(experiment, 'ID', '_', 1)

# display the dataset
req.display_experiment(experiment)

# Request a data using tags
#raw_dataset = req.get_dataset(experiment, name="data")
#raw_data_list = req.get_data(raw_dataset, "Population=population1 AND ID=001")
raw_data_list = req.query(experiment, 'data', "Population=population1 AND ID=001")
print("query result:")
for raw_data in raw_data_list:
    print('\t'+raw_data.name)
