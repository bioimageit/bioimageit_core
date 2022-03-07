class ConfigError(Exception):
    """Raised when an error happen when an operation is made on the configuration"""

    pass


class DataServiceError(Exception):
    """Raised when an error happen in the metadata database"""

    pass


class DataQueryError(Exception):
    """Raised when an error happen in the metadata query"""

    pass


class ToolNotFoundError(Exception):
    """Raised when a process is not found"""

    pass


class ToolsServiceError(Exception):
    """Raised when an error happen when running a process"""

    pass


class RunnerExecError(Exception):
    """Raised when an error occur during a runner execution"""

    pass
