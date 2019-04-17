from .metadata import BiMetaData
import os

class BiData(BiMetaData): 
    """Abstract class that store a data metadata"""
    def __init__(self, md_file_url : str):
        BiMetaData.__init__(self, md_file_url)
        self._objectname = "BiData"  

    def url(self) -> str:
        file = self.metadata["common"]['url']
        if os.path.isfile(file):
            return file
        else:    
            return os.path.join(self.md_file_path(), file)

    def url_as_stored(self) -> str:
        return self.metadata["common"]['url']   

    def name(self) -> str:
        return self.metadata["common"]['name']  

    def author(self) -> str:
        return self.metadata["common"]['author']   

    def createddate(self) -> str:
        return self.metadata["common"]['createddate']          

    def display(self):
        super(BiData, self).display()  
        print('Data: ' + self._md_file_url)
        print('Common ---------------')
        print('Name: ' + self.metadata["common"]['name'])
        print('Url: ' + self.metadata["common"]['url'])
        print('Author: ' + self.metadata["common"]['author'])
        print('Datatype: ' + self.metadata["common"]['datatype'])
        print('Created Date: ' + self.metadata["common"]['createddate'])
        print('Origin ---------------')    
        print('Type: ' + self.metadata["origin"]['type'])
        
class BiRawData(BiData):
    """Class to store and manipulate RawData metadata"""
    def __init__(self, md_file_url : str):
        self._objectname = "BiRawData"
        BiData.__init__(self, md_file_url)

    def tag(self, key: str):
        if 'tags' in self.metadata:
            if key in self.metadata['tags']:
                return self.metadata['tags'][key]
        return ''  

    def set_tag(self, key: str, value: str):
        if 'tags' not in self.metadata:
            self.metadata['tags'] = dict()
        self.metadata['tags'][key] = value

    def display(self): 
        super(BiRawData, self).display()
        print('')

class BiProcessedData(BiData):
    """Class to store and manipulate ProcessedData metadata"""
    def __init__(self, md_file_url : str):
        self._objectname = "BiProcessedData"
        BiData.__init__(self, md_file_url)

    def display(self): 
        super(BiProcessedData, self).display()  
        print('Runurl: ' + self.metadata["origin"]['runurl'])
        print('')
 