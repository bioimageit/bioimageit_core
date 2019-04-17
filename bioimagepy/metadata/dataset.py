from .metadata import BiMetaData
from .data import BiData, BiRawData, BiProcessedData
import os

class BiDataSet(BiMetaData):
    """Abstract class that store a dataset metadata"""
    def __init__(self, md_file_url : str):
        BiMetaData.__init__(self, md_file_url)
        self._objectname = "BiDataSet"

    def name(self) -> str:
        if 'name' in self.metadata:
            return self.metadata["name"]
        else:
            return ''

    def size(self) -> int:
        if 'urls' in self.metadata:
            return len(self.metadata["urls"]) 
        else:
            return 0

    def urls(self) -> list:
        if 'urls' in self.metadata:
            return self.metadata["urls"]
        else:
            return []    

    def url(self, i: int) -> str:
        return self.metadata["urls"][i]

    def data(self, i: int) -> BiData:
        return BiData(os.path.join(self.md_file_path(), self.url(i)))  


class BiRawDataSet(BiDataSet):
    """Class that store a dataset metadata for RawData"""
    def __init__(self, md_file_url : str):
        BiDataSet.__init__(self, md_file_url)
        self._objectname = 'BiRawDataSet'

    def raw_data(self, i: int) -> BiRawData:
        return BiRawData(os.path.join(self.md_file_path(), self.url(i)))
 
    def add_data(self, md_file_url: str):
        if 'urls' in self.metadata:
            self.metadata['urls'].append(md_file_url)
        else:
            self.metadata['urls'] = [md_file_url]              
         

class BiProcessedDataSet(BiDataSet):
    """Class that store a dataset metadata for ProcessedData"""
    def __init__(self, md_file_url : str):
        BiDataSet.__init__(self, md_file_url)
        self._objectname = "BiProcessedDataSet"    

    def processed_data(self, i: int) -> BiProcessedData:
        return BiProcessedData(os.path.join(self.md_file_path(), self.url(i)))        
        