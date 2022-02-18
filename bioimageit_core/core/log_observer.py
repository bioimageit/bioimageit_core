import sys
import os
import datetime
from .observer import Observer


class LogObserver(Observer):
    """Observer that write messages in txt file

    The log observer implements the BioImageIT logs in txt file. For each session there is one new
    log file with the date time, and one extra file per job

    Parameters
    ----------
    log_dir: str
        Path of the directory where the log are saved

    """

    def __init__(self, log_dir):
        super().__init__()
        self.job_files = {}
        self.log_dir = log_dir
        # create the main txt file
        self.log_file_id = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = os.path.join(self.log_dir, f'log{self.log_file_id}.txt')
        with open(self.log_file, 'a') as f:
            f.write('BioImageIT log\n')

    def new_job(self, job_id: int):
        """Add a new job id

        Parameters
        ----------
        job_id: int
            unique ID of the new job

        """
        self.jobs_id.append(job_id)
        self.job_files[job_id] = os.path.join(self.log_dir,
                                              f'log{self.log_file_id}_job{job_id}.txt')
        with open(self.job_files[job_id], 'a') as f:
            f.write(f'BioImageIT log job{job_id}\n')

    def notify(self, message: str, job_id: int = 0):
        """Function called by the observable to notify or log any information

        Parameters
        ----------
        message: str
            Information message
        job_id: int
            unique ID of the job. 0 is main app, and positive is a subprocess

        """
        if job_id == 0:
            with open(self.log_file, 'a') as f:
                f.write(f'{message}\n')
        else:
            with open(self.job_files[job_id], 'a') as f:
                f.write(f'{message}\n')

    def notify_warning(self, message: str, job_id: int = 0):
        """Function called by the observable to warn

        Parameters
        ----------
        message
            Warning message
        job_id: int
            unique ID of the job. 0 is main app, and positive is a subprocess

        """
        if job_id == 0:
            with open(self.log_file, 'a') as f:
                f.write(f'WARNING: {message}\n')
        else:
            with open(self.job_files[job_id], 'a') as f:
                f.write(f'WARNING: {message}\n')

    def notify_error(self, message: str, job_id: int = 0):
        """Function called by the observable to warn

        Parameters
        ----------
        message
            Warning message
        job_id: int
            unique ID of the job. 0 is main app, and positive is a subprocess

        """
        if job_id == 0:
            with open(self.log_file, 'a') as f:
                f.write(f'ERROR: {message}\n')
        else:
            with open(self.job_files[job_id], 'a') as f:
                f.write(f'ERROR: {message}\n')

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
        if job_id == 0:
            with open(self.log_file, 'a') as f:
                f.write(f'{message}, progress: {progress}\n')
        else:
            with open(self.job_files[job_id], 'a') as f:
                f.write(f'{message}, progress: {progress}\n')
