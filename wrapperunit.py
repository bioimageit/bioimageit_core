import sys
import os
from pathlib import Path

from bioimageit_core.core.config import ConfigAccess
from bioimageit_core.wrapperunit.wrapperunit import WrapperUnit

if __name__ == '__main__':

    # parse args
    # xml input
    wrapper_file_or_dir = ''
    if len(sys.argv) > 1:
        wrapper_file_or_dir = sys.argv[1]

    bioimageit_core_dir = os.path.join(os.path.dirname(
        os.path.realpath(__file__)))
    package_dir = Path(bioimageit_core_dir).parent
    config_file = os.path.join(package_dir, 'config.json')
    if len(sys.argv) > 2:
        config_file = sys.argv[2]

    # run toolboxes build
    ConfigAccess(config_file)
    unittesting = WrapperUnit()
    unittesting.run(wrapper_file_or_dir)
