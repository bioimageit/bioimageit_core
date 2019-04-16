from .metadata import BiMetaData

class BiData(BiMetaData): 
    """Abstract class that store a data metadata"""
    def __init__(self, md_file_url : str):
        BiMetaData.__init__(self, md_file_url)
        self._objectname = "BiData"  

    def url(self) -> str:
        return self.metadata["common"]['url']             

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
 