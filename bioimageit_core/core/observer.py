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

    def __init__(self, debug=True):
        self.jobs_id = []
        self.debug = debug

    def new_job(self, job_id: int):
        """Add a new job id

        Parameters
        ----------
        job_id: int
            unique ID of the new job

        """
        self.jobs_id.append(job_id)

    def notify(self, message: str, job_id: int = 0):
        """Function called by the observable to notify or log any information

        Parameters
        ----------
        message: str
            Information message
        job_id: int
            unique ID of the job. 0 is main app, and positive is a subprocess

        """
        prefix = ''
        if job_id > 0:
            prefix = f'job {job_id}:'
        print(f'{prefix} {self.COL_G} {message} {self.COL_W}')

    def notify_warning(self, message: str, job_id: int = 0):
        """Function called by the observable to warn

        Parameters
        ----------
        message
            Warning message
        job_id: int
            unique ID of the job. 0 is main app, and positive is a subprocess

        """
        prefix = ''
        if job_id > 0:
            prefix = f'job {job_id}:'
        print(f'{prefix} {self.COL_O} WARNING: {message} {self.COL_W}')

    def notify_error(self, message: str, job_id: int = 0):
        """Function called by the observable to warn

        Parameters
        ----------
        message
            Warning message
        job_id: int
            unique ID of the job. 0 is main app, and positive is a subprocess

        """
        prefix = ''
        if job_id > 0:
            prefix = f'job {job_id}:'
        print(f'{prefix} {self.COL_R} ERROR: {message} {self.COL_W}')
        if job_id == 0 and self.debug:  # TODO remove this (only for debugging)
            sys.exit()

    def notify_progress(self, progress: int, message: int = '', job_id: int = 0):
        """Function called by the observable to notify progress

        Parameters
        ----------
        progress
            Data describing the progress
        message
            Message to describe the progress step
        job_id: int
            unique ID of the job. 0 is main app, and positive is a subprocess

        """
        prefix = ''
        if job_id > 0:
            prefix = f'job {job_id}:'
        print(f'{prefix} {self.COL_B} {message}, progress: {progress} {self.COL_W}')


class Observable:
    """Define an object that can be observed

    Objects inheriting from this object can be observed
    by an Observer

    """
    def __init__(self):
        self._observers = []
        self._progress_message = ''
        self.job_count = 0

    def new_job(self):
        """Create a new job

        Generate a new job ID and notify all the observers of this new job

        """
        self.job_count += 1
        for observer in self._observers:
            observer.new_job(self.job_count)
        return self.job_count

    def observers_count(self):
        """Get the number of observers"""
        return len(self._observers)

    def remove_observers(self):
        self._observers.clear()

    def add_observer(self, observer: Observer):
        """Add an observer

        Parameters
        ----------
        observer
            ProgressObserver to add

        """
        self._observers.append(observer)

    def notify(self, message: str, job_id: int = 0):
        """Notify observers any information

        Parameters
        ----------
        message
            Information message
        job_id: int
            unique ID of the job. 0 is main app, and positive is a subprocess

        """
        for observer in self._observers:
            observer.notify(message, job_id)

    def notify_warning(self, message: str, job_id: int = 0):
        """Notify observers any warning

        Parameters
        ----------
        message
            Warning message
        job_id: int
            unique ID of the job. 0 is main app, and positive is a subprocess

        """
        for observer in self._observers:
            observer.notify_warning(message, job_id)

    def notify_error(self, message: str, job_id: int = 0):
        """Notify observers any error

        Parameters
        ----------
        message
            Error message
        job_id: int
            unique ID of the job. 0 is main app, and positive is a subprocess

        """
        for observer in self._observers:
            observer.notify_error(message, job_id)

    def notify_progress(self, progress: int, message: str = '', job_id: int = 0):
        """Notify observers computing progress

        Parameters
        ----------
        progress
            Percentage of progress
        message
            Message to describe the progress step
        job_id: int
            unique ID of the job. 0 is main app, and positive is a subprocess

        """
        for observer in self._observers:
            observer.notify_progress(progress, message, job_id)
