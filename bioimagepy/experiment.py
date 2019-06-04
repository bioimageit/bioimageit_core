# -*- coding: utf-8 -*-
"""experiment module.

This module contains the BiExperiment class that allows to read/write and query
an experiment metadata, and a set of function to manipulate experiment metadata

Example
-------
    Here is an example of how to create an experiment and add data to it:

        >>> import bioimagepy.metadata.experiment as experiment
        >>> myexperiment = experiment.create('myexperiment', 'Sylvain Prigent', './' )
        >>> experiment.import_data(experiment_path: str, data_url: str, name: str, author: str, datatype: str, createddate: str = 'now', copy_data: bool = True)
        >>> experiment.import_dir(experiment_path: str, dir_path: str, author: str, datatype: str, createddate: str = 'now', copy_data: bool = True)
        >>> myexperiment.addTag('condition1')
        >>> myexperiment.addTags(['condition1, condition2'])
        >>> myexperiment.display()

Classes
-------
BiExperiment

Methodes
--------
create
import_data
import_dir
tag_rawdata_from_name
tag_rawdata_using_seperator
query
query_single

Todo
----
    * Write a full example (cf tutorial) in this documentation
    * Write manipulation functions: import, tag...
    * add a recursive option for import_dir

"""

from .metadata import BiMetaData, BiRawData, BiRawDataSet, BiProcessedDataSet
import os
import errno
import datetime
from shutil import copyfile
import re
from prettytable import PrettyTable
  
class BiExperiment(BiMetaData):
    """Class that allows to manipulate experiment metadata.

    A BiExperiment object behave as a container for an experiment 
    metadata. It read only the basic information stored in the 
    experiment.md.json metadata files and methods allows to 
    read/write and manipulate datasets and data information

    Parameters
    ----------
        md_file_url (str): Path of the experiment.md.json file.

    Attributes
    ----------
        metadata (tuple): json metadata description.

    """ 

    def __init__(self, md_file_url: str):
  
        BiMetaData.__init__(self, md_file_url)
        self._objectname = 'BiExperiment'

    def set_name(self, name: str):
        """set the experiment name

        Parameters
        ----------
        name
            The experiment name

        """

        self.metadata['information']['name'] = name

    def name(self) -> str:
        """get the experiment name

        Returns
        ----------
        str
            The experiment name

        """

        return self.metadata['information']['name']
  
    def set_author(self, author: str):
        """set the experiment author

        Returns
        ----------
        author
            The experiment author

        """

        self.metadata['information']['author'] = author    

    def author(self) -> str:
        """get the experiment author

        Returns
        ----------
        str
            The experiment author

        """

        return self.metadata['information']['author']

    def createddate(self) -> str:
        """get the experiment created date

        Returns
        ----------
        str
            The experiment created date

        """

        return self.metadata['information']['createddate']

    def set_createddate(self, date: str):
        """set the experiment created date

        Parameters
        ----------
        date
            The experiment created date

        """

        self.metadata['information']['createddate'] = date

    def rawdataset_url(self) -> str:
        """get the experiment raw dataset url

        Returns
        ----------
        str
            The experiment raw dataset url

        """

        return self.metadata['information']['rawdataset']  

    def rawdataset(self) -> BiRawDataSet:
        """get the experiment raw dataset

        Returns
        ----------
        BiRawDataSet
            The experiment raw dataset

        """

        return BiRawDataSet( os.path.join(self.md_file_path(), self.metadata['rawdataset']) )

    def processeddatasets_size(self) -> int:
        """Get the number of processed dataset in the experiment

        Returns
        -------
        int
            The number of processed dataset in the experiment

        """

        return len(self.metadata['processeddatasets']) 

    def processeddataset_url(self, i: int) -> str:
        """Get the url of a processed dataset

        Parameters
        ----------
        i
            Index of the processed dataset

        Returns
        -------
        str
            URL of the processed dataset

        """

        return self.metadata['processeddatasets'][i]  

    def processeddataset_urls(self) -> list:
        """Get the urls of all the processed datasets

        Returns
        -------
        list
            URLs of the processed datasets

        """

        return self.metadata['processeddatasets']   

    def processeddataset(self, i: int) -> BiProcessedDataSet:
        """Get a processed dataset

        Parameters
        ----------
        i
            Index of the processed dataset

        Returns
        -------
        BiProcessedDataSet
            Processed dataset in a BiProcessedDataSet object

        """

        return BiProcessedDataSet( os.path.join(self.md_file_path(), self.metadata['processeddatasets'][i]) )

    def clear_tags(self):
        """Remove all the tags

        """

        self.metadata['tags'] = []

    def tags_size(self) -> int:
        """Get the number of tags

        Returns
        -------
        int
            Number of tags

        """

        return len(self.metadata['tags'])

    def tags(self) -> list:
        """Get the tags

        Returns
        -------
        list
            The list of tags

        """

        if 'tags' in self.metadata: 
            return self.metadata['tags']
        else:
            return []    

    def tag(self, i: int) -> str:
        """Get a tag

        Parameters
        ----------
        i
            Index of the tag

        Returns
        -------
        str
            The tag name

        """
        
        return self.metadata['tags'][i]   

    def add_tag(self, tag: str):
        """Add a tag

        Parameters
        ----------
        tag
            The tag name

        """

        if 'tags' in self.metadata:
            self.metadata['tags'].append(tag) 
        else:
            self.metadata['tags'] = [tag]  

    def set_tag(self, tag: str):
        """Set a tag 

        Same as tags exept that it doen's add the tag if it
        already exists

        Parameters
        ----------
        tag
            The tag name

        """

        if 'tags' in self.metadata:
            if tag not in self.metadata['tags']:
                self.metadata['tags'].append(tag) 
        else:
            self.metadata['tags'] = [tag]          

    def add_tags(self, tags: list):
        """Add a list of tags

        Parameters
        ----------
        tags
            The tags names list

        """

        for tag in tags:
            self.metadata['tags'].append(tag) 

    def display(self):
        """Display inherited from BiObject"""

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
        bi_rawdataset = self.rawdataset()
        for i in range(bi_rawdataset.size()):

            bi_rawdata = bi_rawdataset.raw_data(i)
            tags_values = []
            for key in tags:
                tags_values.append(bi_rawdata.tag(key))
            t.add_row( [ bi_rawdata.name() ] + tags_values + [ bi_rawdata.author(), bi_rawdata.createddate() ] )
        print(t)                             
           

def create(name: str, author: str, path: str) -> BiExperiment:
    """Create an experiment

    Create an empty experiment in the directory specified in the args
    with the informations given in the args

    Parameters
    ----------
    name
        The name of the experiment.
    author
        The name of the person who created the experiment.
    path
        The directory where the experiment files will be stored.

    Returns
    -------
    BiExperiment
        The object containing the experiment.

    Raises
    ------
    FileNotFoundError
        If the experiment path does not exists.

    """
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
    """Import data to an experiment

    This import a single data to the experiment and tag it with the specified metadata

    Parameters
    ----------
    experiment
        The experiment where the data has to be added.
    data_url
        The URL of the data to import
    name
        Name of the data
    author
        Author of the data
    datatype
        The datatype (image, txt...)  
    createddate
        The data creation date  
    copy_data                
        If True, the data is copied into the Experiment folder. Otherwise, only the 
        metadata will be created in the Experiment folder. The second case is 'dangerous'
        if the data URL is not a permanent URL

    Raises
    ------
        FileNotFoundError: if the experiment path does not exists.

    """

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
    """Import data from a directory to an experiment

    This import a set of data to the experiment and tag it with the specified metadata

    Parameters
    ----------
    experiment
        The experiment where the data has to be added.
    dir_path
        The URL of the directory to import
    filter
        Regular expression to filter the files to import from the directory    
    author
        Author of the data
    datatype
        The datatype (image, txt...)  
    createddate
        The data creation date  
    copy_data                
        If True, the data is copied into the Experiment folder. Otherwise, only the 
        metadata will be created in the Experiment folder. The second case is 'dangerous'
        if the data URL is not a permanent URL

    Raises
    ------
        FileNotFoundError: if the experiment path does not exists.

    """
       
    files = os.listdir(dir_path)
    for file in files:
        r1 = re.compile(filter) # re.compile(r'\.tif$')
        if r1.search(file):
            data_url = os.path.join(dir_path, file) 
            import_data(experiment, data_url, file, author, datatype, createddate, copy_data)

def tag_rawdata_from_name(experiment: BiExperiment, tag: str, values: list):
    """Tag an experiment raw data using file name

    Parameters
    ----------
    experiment
        The experiment containing the rawdata.
    tag
        The name (or key) of the tag to add to the data
    values
        List of possible values for the tag to find in the filename    

    """

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
    """Tag an experiment raw data using file name and separator

    Parameters
    ----------
    experiment
        The experiment containing the rawdata.
    tag
        The name (or key) of the tag to add to the data
    separator
        The character used as a separator in the filename (ex: _)    
    value_position
        Position of the value to extract with respect to the separators    

    """
    
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

    Parameters
    ----------
    experiment
        The experiment containing the data.
    query
        String query with the key=value format.    
    
    """
    
    queries = re.split(' AND ',query)

    # initially all the rawdata are selected
    selected_list = experiment.rawsatadet().to_list()

    # run all the AND queries on the preselected dataset
    for q in queries:
        selected_list = query_single(selected_list, q) 
    return selected_list    

def query_single(search_list: list, query: str) -> list:
    """query internal function
    
    Search if the query is on the search_list

    Parameters
    ----------
    search_list
        data search list
    query
        String query with the key=value format. No 'AND', 'OR'...    
    
    """
    
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

#def query(experiment: BiExperiment, dataset_name: str,  query: str) -> list:
#    # TODO: Implement this query
#    return []
