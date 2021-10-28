import sys
import os
import json
from pathlib import Path
from bioimageit_core.toolboxes import Toolboxes
from bioimageit_core.config import ConfigAccess


def read_json(md_uri: str):
    """Read the metadata from the a json file"""
    if os.path.getsize(md_uri) > 0:
        with open(md_uri) as json_file:
            return json.load(json_file)


def write_json(metadata: dict, md_uri: str):
    """Write the metadata to the a json file"""
    with open(md_uri, 'w') as outfile:
        json.dump(metadata, outfile, indent=4)


if __name__ == '__main__':

    # parse args
    user_name = "unknown"
    runner_name = "CONDA"
    if len(sys.argv) > 1:
        user_name = sys.argv[1]
    if len(sys.argv) > 2:
        runner_name = sys.argv[2]    

    runner_name = runner_name.upper()

    # create the config file from config_sample.json
    bioimagepy_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    package_dir = Path(bioimagepy_dir).parent

    config_json = read_json(os.path.join(bioimagepy_dir, 'config_sample.json'))
    config_json["process"]["xml_dirs"] = [ os.path.join(package_dir,
                                                        "toolboxes", "tools")]
    config_json["process"]["categories"] = os.path.join(package_dir,
                                                        "toolboxes",
                                                        "toolboxes.json")
    config_json["process"]["tools"] = os.path.join(package_dir, "toolboxes",
                                                   "tools.json")
    config_json["runner"]["service"] = runner_name
    if runner_name == 'DOCKER':
        config_json["runner"]["working_dir"] = os.path.join(package_dir, "userdata")
    config_json["gui"] = {"tmp": os.path.join(package_dir, "userdata")}
    config_json["user"]["name"] = user_name
    config_json["formats"]["file"] = os.path.join(package_dir, "formats.json")
    config_json["apps"] = {}
    config_json["install_dir"] = str(package_dir)
    config_json["runner"]["working_dir"] = os.path.join(package_dir, "userdata")
    if os.name == 'nt' :
        config_json["apps"]["runner"] = os.path.join(package_dir, "runnerapp.bat")
        config_json["apps"]["processing"] = os.path.join(package_dir, "data_processing.bat")
        config_json["apps"]["viewer"] = os.path.join(package_dir, "viewer.bat")
        config_json["runner"]["condash"] = os.path.join(package_dir, "Miniconda3", "condabin", "conda.bat")
    else :
        config_json["apps"]["runner"] = os.path.join(package_dir, "BioImageIT-Runner.sh")
        config_json["apps"]["processing"] = os.path.join(package_dir, "BioImageIT-toolboxes.sh")
        config_json["apps"]["viewer"] = os.path.join(package_dir, "BioImageIT-Viewer.sh")
        config_json["runner"]["condash"] = os.path.join(package_dir, "miniconda3", "etc", "profile.d", "conda.sh")
    config_file = os.path.join(package_dir, 'config.json')
    write_json(config_json, config_file)

    # run toolboxes build
    ConfigAccess(config_file)
    builder = Toolboxes()
    builder.build()
