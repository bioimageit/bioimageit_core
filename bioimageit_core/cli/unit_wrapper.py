import argparse
from bioimageit_core.wrapperunit import WrapperUnit
from bioimageit_core import ConfigAccess

from bioimageit_formats import FormatsAccess

def main():
    parser = argparse.ArgumentParser(description = 'stracking DoG dectection')
    parser.add_argument('-c', '--config', help = 'BioImageIT configuration file')
    parser.add_argument('-f', '--file', help = 'wrappers dir or single wrapper (xml) file')
    parser.add_argument('-p', '--parse', help = 'Set to one to test only the parsing of wrappers')
    args = parser.parse_args()
    
    config_file = args.config
    xml_file = args.file
    parse_only = False
    if int(args.parse) > 0:
        parse_only = True
    
    ConfigAccess(config_file)
    FormatsAccess(ConfigAccess.instance().config['formats']['file'])

    unit_obj = WrapperUnit(config_file)
    unit_obj.run(xml_file, parse_only)
    unit_obj.print_summary()
    

if __name__ == "__main__":
    main()
