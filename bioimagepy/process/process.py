import os
import xml.etree.ElementTree as ET


class BiProcess(): 
    """Abstract class that store a process information"""
    def __init__(self, xml_file_url : str):
        self._objectname = "BiProcess"
        self._xml_tree = ET.parse(xml_file_url)  


 