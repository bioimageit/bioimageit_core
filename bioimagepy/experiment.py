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

"""

from .metadata import BiMetaData, BiData, BiRawData, BiProcessedData, BiRawDataSet, BiProcessedDataSet
from .core import BiObject, BiProgressObserver
from .process import BiProcessParser, BiProcessInfo
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
        self._rawdataset = None

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

        if self._rawdataset:
            return self._rawdataset
        else:
            self._rawdataset = BiRawDataSet( os.path.join(self.md_file_path(), self.metadata['rawdataset']) )    
            return self._rawdataset 

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

    def processeddataset_names(self) -> list:
        """Get the urls of all the processed datasets

        Returns
        -------
        list
            URLs of the processed datasets

        """

        urls = self.metadata['processeddatasets'] 
        names = []
        for url in urls:
            names.append( url.replace("/processeddataset.md.json", "") )

        return names   


    def processeddataset_by_name(self, name: str) -> BiProcessedData:
        """Get a processed dataset

        Parameters
        ----------
        name
            Name of the processed dataset

        Returns
        -------
        BiProcessedDataSet
            Processed dataset in a BiProcessedDataSet object

        """
        i = -1
        for dataset_url in self.metadata['processeddatasets']:
            i += 1
            if name in dataset_url:
                return self.processeddataset(i)
        return None     


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
        if 'tags' in self.metadata:
            return len(self.metadata['tags'])
        else:
            return 0    

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

    def to_table(self, dataset: str):
        if dataset == "data":
            return self._to_table_data()
        else:
            processeddataset = self.processeddataset_by_name(dataset)
            process_url = processeddataset.process_url()
            process_info = BiProcessParser(process_url).parse()

            if process_info.type == 'sequential':
                return self._to_table_sequential(processeddataset, process_info)
            else:
                return self._to_table_merge(processeddataset, process_info)          

    def _to_table_data(self):
        table = []
        tags = list()   
        header = list()
        header.append("Name") 
        if 'tags' in self.metadata:  
            tags = self.metadata['tags'] 
        for tag in tags:
            header.append(tag)
        header.append('Author')   
        header.append('Created date')  
        table.append( header ) 
        bi_rawdataset = self.rawdataset()
        for i in range(bi_rawdataset.size()):
            bi_rawdata = bi_rawdataset.raw_data(i)
            tags_values = []
            for key in tags:
                tags_values.append(bi_rawdata.tag(key))
            table.append( [ bi_rawdata.name() ] + tags_values + [ bi_rawdata.author(), bi_rawdata.createddate() ] )   
        return table    

    def _to_table_sequential(self, processeddataset: BiProcessedDataSet, process_info: BiProcessInfo):
        table = []
        for i in range(self.rawdataset().size()+1):
            array = ['', '']
            for o in range(len(process_info.outputs)):
                array.append('')   
            for o in range(len(self.tags())):
                array.append('')       
            table.append(array)

        # headers
        table[0][0] = ''
        table[0][1] = 'Name'
        count = 1
        for tag in self.tags():
            count += 1
            table[0][count] = tag
        for output in process_info.outputs:
            count += 1
            table[0][count] = output.description 

        # data
        for i in range(self.rawdataset().size()):

            raw_info = self.rawdataset().raw_data(i)

            # thumbnail
            table[i+1][0] = raw_info.url_as_stored()
            
            # name
            table[i+1][1] = raw_info.name()
            
            # tags
            for t in range(self.tags_size()):
                table[i+1][t+2] = raw_info.tag(self.tag(t))

            offset = 2 + self.tags_size()   

            # search results
            for j in range(processeddataset.size()):
                processed_info = processeddataset.processed_data(j)
                raw_info_p = processed_info.origin_raw_data()  

                #print('test output', processed_info.name(), raw_info_p.name())

                if ( raw_info_p.name() == raw_info.name() ):
                    outIdx = offset-1
                    for output in process_info.outputs:
                        #print('output name', output.name)
                        outIdx +=1
                        #print('test output', output.name, processed_info.metadata['origin']['output']['name'])
                        if processed_info.metadata['origin']['output']['name'] == output.name:
                            #print('match output', output.name, processed_info.metadata['origin']['output']['name'])
                            if processed_info.datatype() == 'image':
                                table[i+1][outIdx] = processed_info.url_as_stored()
                            elif processed_info.datatype() == 'number':
                                table[i+1][outIdx] = processed_info.url_as_stored()
                            elif processed_info.datatype() == 'array':
                                table[i+1][outIdx] = processed_info.url_as_stored()
                            elif processed_info.datatype() == 'table':
                                table[i+1][outIdx] = processed_info.url_as_stored()
                            break

        return table                    
                         
    def _to_table_merge(self, processeddataset: BiProcessedDataSet, process_info: BiProcessInfo):
        table = []

        # header
        labels = ["Name"]
        for output in process_info.outputs:
            labels.append(output.description)
        table.append(labels)
            
        # data
        line_data = []
        for j in range(processeddataset.size()):
            processed_data = processeddataset.processed_data(j)        
            oID = 0
            for output in process_info.outputs:
                oID += 1
                if processed_data.metadata['origin']['output']['label'] == output.description:
                    if processed_data.metadata['origin']['output']['label'] == output.description:
                        if processed_data.datatype() == 'image': 
                            thumbInfo = dict()
                            thumbInfo['row'] = 0
                            thumbInfo['column'] = oID
                            thumbInfo['processeddata'] = processed_data
                            #self.thumbnailList.append(thumbInfo)
                            #self.set_thumbnail(0, oID, processed_data, processed_data.thumbnail())
                            line_data.append(processed_data.url())     
                        elif processed_data.datatype() == 'number':
                            with open(processed_data.url(), 'r') as content_file:
                                p = content_file.read() 
                                line_data.append(p)
                        elif processed_data.datatype() == 'array':
                            with open(processed_data.url(), 'r') as content_file:
                                p = content_file.read() 
                                line_data.append(p)
                        elif processed_data.datatype() == 'table':
                            line_data.append(processed_data.url())
                        else:
                            line_data.append('')       
            table.append(line_data)
        return table    


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
    bi_rawdataset = experiment.rawdataset()  
    bi_rawdataset.add_data_url(md_file_url_relative)
    bi_rawdataset.write()

    return md_file_url
         
class BiExperimentImport(BiObject):
    """Import data to an experiment

    This import multiple data from a directory to a experiment. This class
    implement the observer/observable design pattern to allow observing the
    import progress

    Raises
    ------
        FileNotFoundError: if the experiment path does not exists.

    """

    def __init__(self):
        super().__init__()
        self._observers = []

    def addObserver(self, observer: BiProgressObserver):
        """Add an observer

        Parameters
        ----------
        observer
            BiProgressObserver to add 

        """

        self._observers.append(observer)

    def import_dir(self, experiment: BiExperiment, dir_path: str, filter: str, author: str, 
                   datatype: str, createddate: str = 'now', copy_data: bool = True):
        """Import the data to the experiment

        Parameters
        ----------
        experiment
            BiExperiment where the data are imported

        dir_path
            Path of the directory containing the data to import

        filter
            Regular expression to filter the images to import

        author
            Name of the data author for the metadata   

        datatype
            Type of the data for the metadata (ex: image)

        createddate
            Date when the data where created for the metadata

        copy_data
            True to copy the data to the Experiment directory, False otherwise                     

        """

        files = os.listdir(dir_path)
        count = 0
        for file in files:
            count += 1
            r1 = re.compile(filter) # re.compile(r'\.tif$')
            if r1.search(file):
                self.notify_observers(int(100*count/len(files)), file)
                data_url = os.path.join(dir_path, file) 
                import_data(experiment, data_url, file, author, datatype, createddate, copy_data)       

    def notify_observers(self, count, file):
        """Notify observer the progress of the import

        Parameters
        ----------
        count
            Purcentage of file processed

        file
            Name of the current processed file as a progress message    

        """

        progress = dict()
        progress['purcentage'] = count
        progress['message'] = file
        for observer in self._observers:
            observer.notify(progress)

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
    bi_rawdataset = experiment.rawdataset()
    for i in range(bi_rawdataset.size()):
        bi_rawdata = bi_rawdataset.data(i)
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
    bi_rawdataset = experiment.rawdataset()
    for i in range(bi_rawdataset.size()):
        bi_rawdata = bi_rawdataset.data(i)
        basename = os.path.splitext(os.path.basename(bi_rawdata.url()))[0]
        splited_name = basename.split(separator)
        value = ''
        if len(splited_name) > value_position:
            value = splited_name[value_position]  
        bi_rawdata.set_tag(tag, value) 
        bi_rawdata.write()   

def query(experiment: BiExperiment, dataset: str, query: str, origin_output_name: str = '') -> list:
    """query a specific dataset of an experiment
    
    In this verion only AND queries are supported (ex: tag1=value1 AND tag2=value2)
    and performed on the data set named dataset
    
    Parameters
    ----------
    experiment
        The experiment containing the data.
    dataset
        Name of the dataset to query    
    query
        String query with the key=value format.    

    Returns
    -------
    list
        List of selected data (md.json files urls are returned) 
    """

    # search the dataset
    if experiment.rawdataset().name() == dataset:
        return searchListToUrl(query_rawdataset(experiment.rawdataset(), query))
    else:
        for i in range(experiment.processeddatasets_size()):
            processeddataset = experiment.processeddataset(i)
            if processeddataset.name() == dataset:
                return searchListToUrl(query_processeddataset(processeddataset,  query, origin_output_name))

    print('Query dataset ', dataset, ' not found')

def searchListToUrl(data: list) -> list:
    """Convert a list of BiExperimentSearchContainer to a list of str (URLs)

    Parameters
    ----------
    data
        List of BiExperimentSearchContainer to convert

    Returns
    -------
    list 
        list of str containing URLs   

    """

    out = []
    for d in data:
        out.append(d.url())
    return out    

def query_rawdataset(rawdataset: BiRawDataSet, query: str) -> list:
    """query on tags
    
    In this verion only AND queries are supported (ex: tag1=value1 AND tag2=value2)
    and performed on the RawData set

    Parameters
    ----------
    rawdataset
        The BiRawDataSet to query.
    query
        String query with the key=value format. 

    Returns
    -------
    list
        List of selected data (md.json files urls are returned)       
    
    """
    
    queries = re.split(' AND ',query)

    # initially all the rawdata are selected
    selected_list = rawDataSetToSearchList(rawdataset)

    if query == '':
        return selected_list

    # run all the AND queries on the preselected dataset
    for q in queries:
        selected_list = query_list_single(selected_list, q) 
    return selected_list    


def rawDataSetToSearchList(rawDataSet: BiRawDataSet) -> list:
    """Convert BiRawDataSet into a list of BiExperimentSearchContainer

    Parameters
    ----------
    rawDataSet
        BiRawDataSet to convert

    Returns
    -------
    list
        List of data as list of BiExperimentSearchContainer    

    """

    search_list = []
    for i in range(rawDataSet.size()):
        data = rawDataSet.data(i)
        searchInfo = BiExperimentSearchContainer()
        searchInfo.set_url( os.path.join(data.md_file_dir(), data.md_file_name()))
        if 'tags' in data.metadata:
            searchInfo.data['tags'] = data.metadata['tags']
        search_list.append(searchInfo)    
    return search_list    


def query_processeddataset(dataset: BiProcessedDataSet,  query: str, origin_output_name: str = '') -> list:
    """Run a query on a BiProcessedDataSet

    Parameters
    ----------
    dataset
        BiProcessedDataSet to query

    query
        Query on tags (ex: 'Population'='population1')

    Returns
    -------
    list
        List of the data (md.json) files urls        

    """

    # get all the tags per data
    pre_list = []
    for i in range(dataset.size()):
        data = dataset.data(i)
        pre_list.append(extract_tags(os.path.join(data.md_file_dir(),data.md_file_name())))

    # remove the data where output origin is not the asked one
    selected_list = []
    if origin_output_name != '':
        for pdata in pre_list:
            data = BiProcessedData(pdata.url())
            if data.origin_output_name() == origin_output_name:
               selected_list.append(pdata) 
    else:
        selected_list = pre_list

    if query == '':
        return selected_list

    # query on tags
    queries = re.split(' AND ',query)

    # run all the AND queries on the preselected dataset
    for q in queries:
        selected_list = query_list_single(selected_list, q) 
    return selected_list 



def query_list(search_list: list, query: str) -> list:
    """query on tags
    
    In this verion only AND queries are supported (ex: tag1=value1 AND tag2=value2)
    and performed on the RawData set

    Parameters
    ----------
    search_list
        data search list (list of BiExperimentSearchContainer)
    query
        String query with the key=value format.    
    
    Returns
    -------
    list
        list of selected BiExperimentSearchContainer

    """
    
    queries = re.split(' AND ',query)

    selected_list = search_list

    for q in queries:
        selected_list = query_list_single(selected_list, q) 
    return selected_list


def query_list_single(search_list: list, query: str) -> list:
    """query internal function
    
    Search if the query is on the search_list

    Parameters
    ----------
    search_list
        data search list (list of BiExperimentSearchContainer)
    query
        String query with the key=value format. No 'AND', 'OR'...    
    
    Returns
    -------
    list
        list of selected BiExperimentSearchContainer

    """

    selected_list = list()  
    
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


class BiExperimentSearchContainer():
    """Container for data queries on tag

    Parameters
    ----------
    data 
        Data are stored in dict as
            data['url] = '/url/of/the/metadata/file.md.json'
            data['tags] = {'tag1'='value1', 'tag2'='value2'}

    """

    def __init__(self):
        self.data = dict()

    def url(self):
        """Returns the data metadata file url"""
        if 'url' in self.data:
            return self.data['url']

    def set_url(self, url: str):
        """Set the data metadata file url"""
        self.data['url'] = url            

    def tag(self, key: str):
        """Get a tag value
        
        Parameters
        ----------
        key
            Tag key

        Returns
        -------
        value
            Value of the tag    
        """
        if key in self.data['tags']:
            return self.data['tags'][key]
        return ''    

def extract_tags(metadata_file: str, current_file: str = '') -> BiExperimentSearchContainer:
    """Get the tags associated to a data file
    
    For any file, this function get the origin files to reach
    a rawdata file and get it associated tags

    Parameters
    ----------
    metadata_file
        md.json file of the data to get the tags

    Returns
    -------
        a BiExperimentSearchContainer with the md.json file url and
        the extracted tags       

    
    """

    if current_file == '':
        current_file = metadata_file  

    origin_data = BiData(metadata_file)
    if origin_data.origin_type() == 'raw':
        origin_rawdata = BiRawData(metadata_file)
        info = dict()
        if 'tags' in origin_rawdata.metadata:
            info = BiExperimentSearchContainer()
            info.data["url"] = current_file
            info.data['tags'] = origin_rawdata.metadata['tags']
            return info
    else:
        origin_processeddata = BiProcessedData(metadata_file) 
        origin_url = origin_processeddata.metadata['origin']['inputs'][0]['url'] 
        origin_file = os.path.join(origin_processeddata.md_file_dir(), origin_url)
        return extract_tags(origin_file, current_file)
