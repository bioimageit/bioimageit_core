import sys
import os
from pathlib import Path

from bioimageit_core.toolboxes import Toolboxes
from bioimageit_core.config import ConfigAccess
from bioimageit_core.process import ProcessAccess

if __name__ == '__main__':

    # parse args
    bioimageit_core_dir = os.path.join(os.path.dirname(
        os.path.realpath(__file__)))
    package_dir = Path(bioimageit_core_dir).parent
    config_file = os.path.join(package_dir, 'config.json')
    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    database_json = ''
    if len(sys.argv) > 2:
        database_json = sys.argv[2]

    # run toolboxes build
    ConfigAccess(config_file)
    builder = Toolboxes()
    builder.build()

    # save the database
    if database_json != '':
        processAccess = ProcessAccess()
        processAccess.export_json(database_json)
