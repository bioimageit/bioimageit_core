import sys


class Observer:
    COL_W = '\033[0m'  # white (normal)
    COL_R = '\033[31m'  # red
    COL_G = '\033[32m'  # green
    COL_O = '\033[33m'  # orange
    COL_B = '\033[34m'  # blue
    COL_P = '\033[35m'  # purple

    """Observer that display messages in the console

    The basic implementation just display the progress in the
    console with 'print'. Please subclass this class to write
    progress in log files or notify a GUI for example

    """

    def __init__(self):
        super().__init__()

    def notify(self, message: str):
        """Function called by the observable to notify or log any information

        Parameters
        ----------
        message
            Information message

        """
        print(f'WARNING: {self.COL_W} {message} {self.COL_W}')

    def notify_warning(self, message: str):
        """Function called by the observable to warn

        Parameters
        ----------
        message
            Warning message

        """
        print(f'WARNING: {self.COL_O} {message} {self.COL_W}')

    def notify_error(self, message: str):
        """Function called by the observable to warn

        Parameters
        ----------
        message
            Warning message

        """
        print(f'ERROR: {self.COL_R} {message} {self.COL_W}')
        sys.exit()

    def notify_progress(self, progress: int, message: int = ''):
        """Function called by the observable to notify progress

        Parameters
        ----------
        progress
            Data describing the progress
        message
            Message to describe the progress step

        """
        print(f'progress: {self.COL_W} {progress} {self.COL_W}')


class Observable:
    """Define an object that can be observed

    Objects inheriting from this object can be observed
    by an Observer

    """

    def __init__(self):
        self._observers = []
        self._progress_message = ''

    def observers_count(self):
        """Get the number of observers"""
        return len(self._observers)

    def add_observer(self, observer: Observer):
        """Add an observer

        Parameters
        ----------
        observer
            ProgressObserver to add

        """
        self._observers.append(observer)

    def notify(self, message: str):
        """Notify observers any information

        Parameters
        ----------
        message
            Information message

        """
        for observer in self._observers:
            observer.notify(message)

    def notify_warning(self, message: str):
        """Notify observers any warning

        Parameters
        ----------
        message
            Warning message

        """
        for observer in self._observers:
            observer.notify_warning(message)

    def notify_error(self, message: str):
        """Notify observers any error

        Parameters
        ----------
        message
            Error message

        """
        for observer in self._observers:
            observer.notify_error(message)

    def notify_progress(self, progress: int, message: str = ''):
        """Notify observers computing progress

        Parameters
        ----------
        progress
            Percentage of progress
        message
            Message to describe the progress step

        """
        for observer in self._observers:
            observer.notify_progress(progress, message)
