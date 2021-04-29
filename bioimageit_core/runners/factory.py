# -*- coding: utf-8 -*-
"""BioImagePy runner service provider.

This module implement the runner service provider

Classes
------- 
RunnerServiceProvider

"""

from bioimageit_core.core.factory import ObjectFactory
from bioimageit_core.runners.service_local import LocalRunnerServiceBuilder
from bioimageit_core.runners.service_conda import CondaRunnerServiceBuilder
#from bioimageit_core.runners.service_singularity import \
#    SingularityRunnerServiceBuilder
#from bioimageit_core.runners.service_allgo import AllgoRunnerServiceBuilder
from bioimageit_core.runners.service_docker import DockerRunnerServiceBuilder
import bioimageit_core.runners.service_condadocker

class RunnerServiceProvider(ObjectFactory):
    def get(self, service_id, **kwargs):
        return self.create(service_id, **kwargs)


runnerServices = RunnerServiceProvider()
runnerServices.register_builder('LOCAL', LocalRunnerServiceBuilder())
runnerServices.register_builder('CONDA', CondaRunnerServiceBuilder())
#runnerServices.register_builder('SINGULARITY',
#                                SingularityRunnerServiceBuilder())
#runnerServices.register_builder('ALLGO', AllgoRunnerServiceBuilder())
runnerServices.register_builder('DOCKER', DockerRunnerServiceBuilder())
runnerServices.register_builder('CONDA_DOCKER',
                                bioimageit_core.runners.service_condadocker.
                                CondaDockerRunnerServiceBuilder())
