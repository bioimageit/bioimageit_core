class ProcessNotFoundError(Exception):
    """Raised when a process is not found"""

    pass


class ProcessServiceError(Exception):
    """Raised when an error happen when running a process"""

    pass
