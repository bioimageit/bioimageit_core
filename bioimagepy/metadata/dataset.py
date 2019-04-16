from .metadata import BiMetaData
from .data import BiData, BiRawData, BiProcessedData
import os

class BiDataSet(BiMetaData):
    """Abstract class that store a dataset metadata"""
    def __init__(self, md_file_url : str):
        BiMetaData.__init__(self, md_file_url)
        self._objectname = "BiDataSet"

    def name(self) -> str:
        return self.metadata["name"]

    def size(self) -> int:
        return len(self.metadata["urls"]) 

    def urls(self) -> list:
        return self.metadata["urls"] 

    def url(self, i: int) -> str:
        return self.metadata["urls"][i]

    def data(self, i: int) -> BiData:
        return BiData(os.path.join(self.md_file_path(), self.url(i)))  


class BiRawDataSet(BiDataSet):
    """Class that store a dataset metadata for RawData"""
    def __init__(self, md_file_url : str):
        BiDataSet.__init__(self, md_file_url)
        self._objectname = "BiRawDataSet"

    def raw_data(self, i: int) -> BiRawData:
        return BiRawData(os.path.join(self.md_file_path(), self.url(i)))
         

class BiProcessedDataSet(BiDataSet):
    """Class that store a dataset metadata for ProcessedData"""
    def __init__(self, md_file_url : str):
        BiDataSet.__init__(self, md_file_url)
        self._objectname = "BiProcessedDataSet"    

    def processed_data(self, i: int) -> BiProcessedData:
        return BiProcessedData(os.path.join(self.md_file_path(), self.url(i)))        
        