import os

from bioimageit_core.core.observer import Observable
from bioimageit_core.core.config import ConfigAccess
from bioimageit_formats import FormatsAccess
from bioimageit_core.containers.tools_containers import Tool
from bioimageit_core.wrapperunit import compare

from bioimageit_core.api import Request
from bioimageit_core.core.exceptions import ToolsServiceError
from bioimageit_core.plugins.tools_local import LocalToolsService


class WrapperUnit(Observable):
    def __init__(self, config_file):
        super().__init__()
        self.req = Request(config_file)
        self.req.connect(init_process=False)
        self.summary = {}

    def run(self, wrapper_file_or_dir: str, parse_only=False):
        if os.path.isfile(wrapper_file_or_dir):
            self.unit_file(wrapper_file_or_dir, parse_only)
        elif os.path.isdir(wrapper_file_or_dir):
            self.unit_dir(wrapper_file_or_dir, parse_only)
        else:
            print('Input wrapper file or dir does not exists!')

    def unit_dir(self, directory_path: str, parse_only):
        for r, d, f in os.walk(directory_path):
            for item in f:
                if '.xml' in item:
                    try:
                        self.unit_file(os.path.join(r, item), parse_only)
                    except:
                        self.notify_warning(f'Error when testing the wrapper: {item}')

    def unit_file(self, xml_path: str, parse_only: bool):
        self.summary[xml_path] = []
        # open the process
        local_tool_service = LocalToolsService()
        try:
            process = local_tool_service.read_tool(xml_path)
        except ToolsServiceError as e:
            self.notify_error(f"Cannot parse the wrapper {xml_path}")  
            self.summary[xml_path].append({'parsing': f'error: {e}'})  
            return  
        self.summary[xml_path].append({'parsing': 'success'})    
        # build the command line
        if not parse_only: 
            args = {}
            for test_id, test in enumerate(process.tests):
                for param in test:
                    if param.type == 'param':
                        param.value = self.format_input_value(
                            process, param.name, param.value
                        )
                        args[param.name] = param.value
                    else:
                        if hasattr(param, "value"):
                            param.value = self.format_output_tmp_value(process, param.name, param.value)
                        else:
                            param.value = self.format_output_tmp_value(process, param.name)

                        args[param.name] = param.value

                # exec the process in tmp dir
                self.req.exec(process, **args)

                # compare and clean the outputs
                for param in test:
                    if param.type == 'output':
                        if param.file != '':
                            # compare
                            if not getattr(compare, param.compare)(
                                param.value, self.format_reference_file(process,
                                                                        param.file)
                            ):
                                self.notify_error(f"Unit test failed for {process.name}")
                                self.summary[xml_path].append({f'test {test_id}': f'{param.name} does not match'})
                            else:
                                self.notify(f"Unit test passed for {process.name}")
                                self.summary[xml_path].append({f'test {test_id}': f'{param.name} success'})
                        # clean
                        os.remove(param.value)

    def print_summary(self):
        num_errors = 0
        for key, value in self.summary.items():
            print(key)
            for output in value:
                out_key = list(output.keys())[0]
                out_value = output[out_key]
                if 'success' not in out_value:
                    num_errors += 1
                    print(f"\t\033[31m{out_key}: {out_value}\033[0m")
                else:
                    print(f"\t\033[32m{out_key}: {out_value}\033[0m")

        print('-- BioImageIT wrappers testing sumary --')
        print(f"Run {len(list(self.summary.keys()))} test, {num_errors} errors")                    

    def format_output_tmp_value(self, process: Tool, name: str, value: str = ""):
        """create the path of the output files"""
        tmp_dir = ConfigAccess.instance().config['workspace']
        for output in process.outputs:
            # output.display()
            if output.name == name and output.io == 'output':
                if output.type == "bioformat" and bool(os.path.splitext(value)[1]):
                    return os.path.join(tmp_dir, value)

                extension = '.' + FormatsAccess.instance().get(output.type).extension
                return os.path.join(tmp_dir, name + extension)
        return name

    def format_reference_file(self, process: Tool, file: str):
        file_dir = os.path.join(
            os.path.dirname(os.path.realpath(process.uri)), 'test-data'
        )
        return os.path.join(file_dir, file)

    def format_input_value(self, process: Tool, name: str, value: str):
        """if the value is an input data, replace the value with full path"""
        file_dir = os.path.join(
            os.path.dirname(os.path.realpath(process.uri)), 'test-data'
        )
        for input_ in process.inputs:
            if input_.name == name and input_.io == 'input':
                return os.path.join(file_dir, value)
        return value
