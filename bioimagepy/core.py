# -*- coding: utf-8 -*-
"""BioImagePy core module.

Contains a set of classes and methods for generic usage

Classes
-------
BiObject


"""

class BiObject:
    """Abstract base class for all object used in the BioImagePy package 
    
    The aim of this class is tho have a common basis for all objects in
    the BioImagePy package and share common operations/information.

    Parameters
    ----------
    _objectname
        Name of the object
    """

    def __init__(self):

        self._objectname = "BiObject"           

    def display(self):
        """Display the class information in console
        
        This method should be reimplemented in each subclass in order
        to ba able to display the class content
        """

        print('BiObjectName: ' + self._objectname)
        print('----------------------')
        

class BiProgressObserver(BiObject):
    def __init__(self):
        super().__init__()
        self._objectname = "BiObserver"  

    def notify(self, data: dict):
        if 'progress' in data:
            print('progress:', data['progress'])
        if 'message' in data:
            print('message:', data['message'])   
        if 'warning' in data:
            print('warning:', data['warning']) 
        if 'error' in data:
            print('error:', data['error'])         
                      