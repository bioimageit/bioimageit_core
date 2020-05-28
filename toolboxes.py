import sys
import os
from bioimagepy.toolboxes import Toolboxes
from bioimagepy.config import ConfigAccess

if __name__ == '__main__':
    
    # parse args
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    # run toolboxes build
    ConfigAccess(config_file)
    builder = Toolboxes()
    builder.build()