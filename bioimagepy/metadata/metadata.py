import os 
import json
from ..core import core
import errno

class BiMetaData(core.BiObject):
    """Abstract class that store a data metadata"""
    def __init__(self, md_file_url : str):
        self._objectname = "BiMetaData"
        self._md_file_url = md_file_url
        self.metadata = {}
        if os.path.isfile(md_file_url):
            self.read()
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), md_file_url) 

    def md_file_path(self) -> str:
        abspath = os.path.abspath(self._md_file_url)
        return os.path.dirname(abspath)

    def read(self):
        if os.path.getsize(self._md_file_url) > 0:
            with open(self._md_file_url) as json_file:  
                self.metadata = json.load(json_file)

    def write(self):
        with open(self._md_file_url, 'w') as outfile:
            json.dump(self.metadata, outfile, indent=4)    

    def display(self):
        super(BiMetaData, self).display()  