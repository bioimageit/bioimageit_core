import datetime

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

    def addObserver(self, observer: ProgressObserver):
        """Add an observer

        Parameters
        ----------
        observer
            ProgressObserver to add 

        """
        self._observers.append(observer)  

    def notify_observers(self, purcentage, message):
        """Notify observer the progress of the import

        Parameters
        ----------
        count
            Purcentage of file processed

        file
            Name of the current processed file as a progress message    

        """
        progress = dict()
        progress['purcentage'] = purcentage
        progress['message'] = message
        for observer in self._observers:
            observer.notify(progress)     

def format_date(date:str):
    if date == 'now':
        now = datetime.datetime.now()
        return now.strftime('%Y-%m-%d')
    else:
        return date  