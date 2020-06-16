import datetime
import os

class ProgressObserver():
    """Observer to display or log a process progress
    
    The basic implementation just display the progress in the 
    console with 'print'. Please subclass this class to write
    progress in log files or notify a GUI for example
    
    """
    def __init__(self):
        super().__init__() 

    def notify(self, data: dict):
        """Function called by the observable to notify progress

        Parameters
        ----------
        data
            Data descibing the progress
        """

        if 'progress' in data:
            print('progress:', data['progress'])
        if 'message' in data:
            print('message:', data['message'])   
        if 'warning' in data:
            print('warning:', data['warning']) 
        if 'error' in data:
            print('error:', data['error'])  


class Observable():
    """Define an object that can be observed

    Objects inheriting from this object can be observed
    by a ProgressObserver

    """
    def __init__(self):
        self._observers = []

    def observers_count(self):
        """Get the number of observers"""
        return len(self._observers)


    def add_observer(self, observer: ProgressObserver):
        """Add an observer

        Parameters
        ----------
        observer
            ProgressObserver to add 

        """
        self._observers.append(observer) 

    def addObserver(self, observer: ProgressObserver):
        """Add an observer (obsolete)

        Parameters
        ----------
        observer
            ProgressObserver to add 

        """
        self._observers.append(observer)  


    def notify_message(self, message: str):
        """Notify observer the progress of the import

        Parameters
        ----------
        count
            Purcentage of file processed

        file
            Name of the current processed file as a progress message    

        """
        progress = dict()
        progress['message'] = message
        self._progress_message = message
        for observer in self._observers:
            observer.notify(progress) 

    def notify_observers(self, progress: int, message: str = ''):
        """Notify observer the progress of the import

        Parameters
        ----------
        progress
            Purcentage progress (in [0,100])

        message
            Progress message   

        """
   
        progress_dict = dict()
        progress_dict['progress'] = progress
        progress_dict['message'] = message
        for observer in self._observers:
            observer.notify(progress_dict)     

def format_date(date:str):
    if date == 'now':
        now = datetime.datetime.now()
        return now.strftime('%Y-%m-%d')
    else:
        return date  

def extract_filename(uri:str):
    pos = uri.rfind(os.sep)
    return uri[pos:]  
     