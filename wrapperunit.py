import sys
import os
from pathlib import Path

from bioimagepy.toolboxes import Toolboxes
from bioimagepy.config import ConfigAccess
from bioimagepy.wrapperunit.wrapperunit import WrapperUnit

if __name__ == '__main__':

    # parse args
    # xml input
    wrapper_file_or_dir = ''
    if len(sys.argv) > 1:
        wrapper_file_or_dir = sys.argv[1]

    bioimagepy_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    package_dir = Path(bioimagepy_dir).parent
    config_file = os.path.join(package_dir, 'config.json')
    if len(sys.argv) > 2:
        config_file = sys.argv[2]

    # run toolboxes build
    ConfigAccess(config_file)
    unittesting = WrapperUnit()
    unittesting.run(wrapper_file_or_dir)
