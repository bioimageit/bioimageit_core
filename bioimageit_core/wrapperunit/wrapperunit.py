import os

from bioimageit_core.core.utils import Observable
from bioimageit_core.core.config import ConfigAccess
from bioimageit_core.process import Process
from bioimageit_core.runner import Runner
from bioimageit_core.core.utils import ProgressObserver
from bioimageit_core.wrapperunit import compare


class WrapperUnit(Observable):
    def __init__(self):
        super().__init__()

    def run(self, wrapper_file_or_dir: str):
        if os.path.isfile(wrapper_file_or_dir):
            self.unit_file(wrapper_file_or_dir)
        elif os.path.isdir(wrapper_file_or_dir):
            self.unit_dir(wrapper_file_or_dir)
        else:
            print('Input wrapper file or dir does not exists!')

    def unit_dir(self, directory_path: str):
        for r, d, f in os.walk(directory_path):
            for item in f:
                if '.xml' in item:
                    self.unit_file(os.path.join(r, item))

    def unit_file(self, xml_path: str):
        # open the process
        process = Process(xml_path)
        # build the command line
        args = []
        for test in process.metadata.tests:
            for param in test:
                if param.type == 'param':
                    args.append(param.name)
                    param.value = self.format_input_value(
                        process, param.name, param.value
                    )
                    args.append(param.value)
                else:
                    args.append(param.name)
                    param.value = self.format_output_tmp_value(process,
                                                               param.name)
                    args.append(param.value)

            # exec the process in tmp dir
            runner = Runner(process)
            runner.add_observer(ProgressObserver())
            runner.exec(*args)

            # compare and clean the outputs
            for param in test:
                if param.type == 'output':
                    if param.file != '':
                        # compare
                        if not getattr(compare, param.compare)(
                            param.value, self.format_reference_file(process,
                                                                    param.file)
                        ):
                            print(
                                '\033[31m'
                                + 'ERROR: test for '
                                + process.metadata.name
                                + ' failed'
                                + '\033[0m'
                            )
                        else:
                            print(
                                '\033[32m'
                                + 'test for "'
                                + process.metadata.name
                                + '" passed'
                                + '\033[0m'
                            )
                    # clean
                    os.remove(param.value)

    def format_output_tmp_value(self, process: Process, name: str):
        """create the path of the output files"""
        tmp_dir = ConfigAccess.instance().config['unittesting']['tmp']
        for output in process.metadata.outputs:
            # output.display()
            if output.name == name and output.io == 'output':
                return os.path.join(tmp_dir, name + '.' + output.type)
        return name

    def format_reference_file(self, process: Process, file: str):
        file_dir = os.path.join(
            os.path.dirname(os.path.realpath(process.uri)), 'test-data'
        )
        return os.path.join(file_dir, file)

    def format_input_value(self, process: Process, name: str, value: str):
        """if the value is an input data, replace the value with full path"""
        file_dir = os.path.join(
            os.path.dirname(os.path.realpath(process.uri)), 'test-data'
        )
        for input_ in process.metadata.inputs:
            if input_.name == name and input_.io == 'input':
                return os.path.join(file_dir, value)
        return value
