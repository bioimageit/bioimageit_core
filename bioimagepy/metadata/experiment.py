# -*- coding: utf-8 -*-
'''experiment module.

This module contains the BiExperiment class that allows to read/write and query
an experiment metadata, and a set of function to manipulate experiment metadata

Example:
    Here is an example of how to create an experiment and add data to it:

        >> import bioimagepy.metadata.experiment as experiment
        >>
        >> myexperiment = experiment.create('myexperiment', 'Sylvain Prigent', './' )
        >> experiment.import_data(experiment_path: str, data_url: str, name: str, author: str, datatype: str, createddate: str = 'now', copy_data: bool = True)
        >> experiment.import_dir(experiment_path: str, dir_path: str, author: str, datatype: str, createddate: str = 'now', copy_data: bool = True)
        >> myexperiment.addTag('condition1')
        >> myexperiment.addTags(['condition1, condition2'])
        >> myexperiment.display()

Todo:
    * Write a full example (cf tutorial) in this documentation
    * Write manipulation functions: import, tag...
    * add a recursive option for import_dir

'''

from .metadata import BiMetaData
from .data import BiRawData
from .dataset import BiRawDataSet, BiProcessedDataSet
import os
import errno
import datetime
from shutil import copyfile
import re
from prettytable import PrettyTable
 
class BiExperiment(BiMetaData):
    '''Class that allows to manipulate experiment metadata.

    A BiExperiment object behave as a container for an experiment 
    metadata. It read only the basic information stored in the 
    experiment.md.json metadata files and methods allows to 
    read/write and manipulate datasets and data information

    Args:
        md_file_url (str): Path of the experiment.md.json file.

    Attributes:
        metadata (tuple): json metadata description.

    ''' 
    def __init__(self, md_file_url: str):
        '''BiExperiment __init__ method.

        The __init__ method load the experiment metadata if the specified 
        input metadata file exists.

        Args:
            md_file_url (str): The url or path of the experiment metadata file.

        '''
        BiMetaData.__init__(self, md_file_url)
        self._objectname = 'BiExperiment'

    def name(self) -> str:
        return self.metadata['information']['name']
  
    def author(self) -> str:
        return self.metadata['information']['author']

    def createddate(self) -> str:
        return self.metadata['information']['createddate']

    def rawsatadet_url(self) -> str:
        return self.metadata['information']['rawdataset']  

    def rawsatadet(self) -> BiRawDataSet:
        return BiRawDataSet( os.path.join(self.md_file_path(), self.metadata['rawdataset']) )

    def processeddatasets_size(self) -> int:
        return len(self.metadata['processeddatasets']) 

    def processeddataset_url(self, i: int) -> str:
        return self.metadata['processeddatasets'][i]  

    def processeddataset_urls(self) -> list:
        return self.metadata['processeddatasets']   

    def processeddataset(self, i: int) -> BiProcessedDataSet:
        return BiRawDataSet( os.path.join(self.md_file_path(), self.metadata['processeddatasets'][i]) )

    def tags_size(self) -> int:
        return len(self.metadata['tags'])

    def tags(self) -> list:
        if 'tags' in self.metadata: 
            return self.metadata['tags']
        else:
            return []    

    def tag(self, i: int) -> str:
        return self.metadata['tags'][i]   

    def add_tag(self, tag: str):
        if 'tags' in self.metadata:
            self.metadata['tags'].append(tag) 
        else:
            self.metadata['tags'] = [tag]  

    def set_tag(self, tag: str):
        if 'tags' in self.metadata:
            if tag not in self.metadata['tags']:
                self.metadata['tags'].append(tag) 
        else:
            self.metadata['tags'] = [tag]          

    def add_tags(self, tags: list):
        for tag in tags:
            self.metadata['tags'].append(tag) 

    def display(self):
        print("--------------------")
        print("Experiment: ")
        print("\tName: " + self.name())
        print("\tAuthor: " + self.author())
        print("\tCreated: " + self.createddate()) 
        print("\tRawDataSet: ")   
        tags = list()    
        if 'tags' in self.metadata:  
            tags = self.metadata['tags']   
        t = PrettyTable(['Name'] + tags + ['Author', 'Created date'])
        bi_rawdataset = self.rawsatadet()
        for i in range(bi_rawdataset.size()):

            bi_rawdata = bi_rawdataset.raw_data(i)
            tags_values = []
            for key in tags:
                tags_values.append(bi_rawdata.tag(key))
            t.add_row( [ bi_rawdata.name() ] + tags_values + [ bi_rawdata.author(), bi_rawdata.createddate() ] )
        print(t)                             
           

def create(name: str, author: str, path: str) -> BiExperiment:
    '''Create an experiment

    Create an empty experiment in the directory specified in the args
    with the informations given in the args

    Args:
        name (str): The name of the experiment.
        author (str): The name of the person who created the experiment.
        path (str): The directory where the experiment files will be stored.

    Returns:
        BiExperiment: The object containing the experiment.

    Raises:
        FileNotFoundError: if the experiment path does not exists.

    '''
    #create the experiment directory
    filtered_name = name.replace(' ', '')
    experiment_path = os.path.join(path, filtered_name)
    if os.path.exists(path):
        os.mkdir( experiment_path )    
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

    #create the data directory
    rawdata_path = os.path.join(experiment_path, 'data')
    rawdataset_md_url = os.path.join(rawdata_path, 'rawdataset.md.json')
    if os.path.exists(experiment_path):
        os.mkdir( rawdata_path )
        open(rawdataset_md_url, 'a').close()
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

    #create the experiment metadata
    # experiment.md.json
    md_file_url = os.path.join(experiment_path, 'experiment.md.json')
    open(md_file_url, 'a').close()
    experiment = BiExperiment(md_file_url)
    information = dict()
    information['name'] = name
    information['author'] = author
    now = datetime.datetime.now()
    information['createddate'] = now.strftime('%Y-%m-%d')
    experiment.metadata['information'] = information
    experiment.metadata['rawdataset'] = 'data/rawdataset.md.json'
    experiment.metadata['processeddatasets'] = []
    experiment.write()

    # rawdataset.md.json
    bi_rawdataset = BiRawDataSet(rawdataset_md_url)
    bi_rawdataset.metadata["name"] = "data"
    bi_rawdataset.metadata["urls"] = []
    bi_rawdataset.write()

    return experiment

def import_data(experiment: BiExperiment, data_url: str, name: str, author: str, datatype: str, createddate: str = 'now', copy_data: bool = True):
    
    experiment_path = experiment.md_file_path() 

    filtered_name = name.replace(' ', '')
    filtered_name, ext = os.path.splitext(filtered_name)
    data_dir_path = os.path.join(experiment_path, 'data')
    md_file_url = os.path.join(data_dir_path, filtered_name + '.md.json')
    md_file_url_relative = filtered_name + '.md.json'
    if os.path.isdir(experiment_path):
        open(md_file_url, 'a').close()
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), md_file_url) 

    # create BiRawData metadata
    bi_data = BiRawData(md_file_url) 
    bi_data.metadata['common'] = dict()  
    bi_data.metadata['common']['name'] = name
    bi_data.metadata['common']['author'] = author
    bi_data.metadata['common']['datatype'] = datatype
    if createddate == 'now':
        now = datetime.datetime.now()
        bi_data.metadata['common']['createddate'] = now.strftime('%Y-%m-%d')
    else:
        bi_data.metadata['common']['createddate'] = createddate  

    bi_data.metadata['origin'] = dict()
    bi_data.metadata['origin']['type'] = 'raw'
    # import data
    if copy_data:
        data_base_name = os.path.basename(data_url)
        copied_data_url = os.path.join(data_dir_path, data_base_name)
        copyfile(data_url, copied_data_url)
        bi_data.metadata['common']['url'] = data_base_name
    else:    
        bi_data.metadata['common']['url'] = data_url 
    bi_data.write()

    # add data to experiment RawDataSet
    bi_rawdataset = experiment.rawsatadet()  
    bi_rawdataset.add_data(md_file_url_relative)
    bi_rawdataset.write()
         
def import_dir(experiment: BiExperiment, dir_path: str, filter: str, author: str, 
               datatype: str, createddate: str = 'now', copy_data: bool = True):
           
    files = os.listdir(dir_path)
    for file in files:
        r1 = re.compile(filter) # re.compile(r'\.tif$')
        if r1.search(file):
            data_url = os.path.join(dir_path, file) 
            import_data(experiment, data_url, file, author, datatype, createddate, copy_data)

def tag_rawdata_from_name(experiment: BiExperiment, tag: str, values: list):
    experiment.set_tag(tag) 
    experiment.write()   
    bi_rawdataset = experiment.rawsatadet()
    for i in range(bi_rawdataset.size()):
        bi_rawdata = bi_rawdataset.raw_data(i)
        for value in values:
            if value in bi_rawdata.name():      
                bi_rawdata.set_tag(tag, value)
                break
        bi_rawdata.write()      

def tag_rawdata_using_seperator(experiment: BiExperiment, tag: str, separator: str, value_position: int):
    experiment.set_tag(tag) 
    experiment.write()   
    bi_rawdataset = experiment.rawsatadet()
    for i in range(bi_rawdataset.size()):
        bi_rawdata = bi_rawdataset.raw_data(i)
        basename = os.path.splitext(os.path.basename(bi_rawdata.url()))[0]
        splited_name = basename.split(separator)
        value = ''
        if len(splited_name) > value_position:
            value = splited_name[value_position]  
        bi_rawdata.set_tag(tag, value) 
        bi_rawdata.write()   

def query(experiment: BiExperiment, query: str) -> list:
    """query on tags
    
    In this verion only AND queries are supported (ex: tag1=value1 AND tag2=value2)
    and performed on the RawData set
     """
    
    queries = re.split(' AND ',query)

    # initially all the rawdata are selected
    selected_list = experiment.rawsatadet().to_list()

    # run all the AND queries on the preselected dataset
    for q in queries:
        selected_list = query_single(selected_list, q) 
    return selected_list    

def query_single(search_list: list, query: str) -> list:
    selected_list = list()  
    # get the query (tag=value)
    
    if "<=" in query:
        splitted_query = query.split('<=')
        if len(splitted_query) != 2:
            print('Error: the query ' + query + ' is not correct. Must be (key<=value)' )
        key = splitted_query[0]
        value = float(splitted_query[1])   
        for i in range(len(search_list)):
            if float(search_list[i].tag(key)) <= float(value):
                selected_list.append(search_list[i]) 

    elif ">=" in query:
        splitted_query = query.split('>=')
        if len(splitted_query) != 2:
            print('Error: the query ' + query + ' is not correct. Must be (key>=value)' )
        key = splitted_query[0]
        value = splitted_query[1]   
        for i in range(len(search_list)):
            if float(search_list[i].tag(key)) >= float(value):
                selected_list.append(search_list[i])
    elif "=" in query:
        splitted_query = query.split('=')
        if len(splitted_query) != 2:
            print('Error: the query ' + query + ' is not correct. Must be (key=value)' )
        key = splitted_query[0]
        value = splitted_query[1]  
        for i in range(len(search_list)):
            if search_list[i].tag(key) == value:
                selected_list.append(search_list[i])
    elif "<" in query:
        splitted_query = query.split('<')
        if len(splitted_query) != 2:
            print('Error: the query ' + query + ' is not correct. Must be (key<value)' )
        key = splitted_query[0]
        value = splitted_query[1]   
        for i in range(len(search_list)):
            if float(search_list[i].tag(key)) < float(value):
                selected_list.append(search_list[i])
    elif ">" in query:            
        splitted_query = query.split('>')
        if len(splitted_query) != 2:
            print('Error: the query ' + query + ' is not correct. Must be (key>value)' )
        key = splitted_query[0]
        value = splitted_query[1]   
        for i in range(len(search_list)):
            if float(search_list[i].tag(key)) > float(value):
                selected_list.append(search_list[i])

    return selected_list        
