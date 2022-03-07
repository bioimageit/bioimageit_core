import os
import sys

from bioimageit_core.core.config import ConfigAccess
from bioimageit_core.process import ProcessAccess

if __name__ == '__main__':

    # parse args
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'config.json')
    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    database_json = ''
    if len(sys.argv) > 2:
        database_json = sys.argv[2]

    # run toolboxes export
    ConfigAccess(config_file)
    processAccess = ProcessAccess()
    processAccess.search()
    processAccess.export_json(database_json)
