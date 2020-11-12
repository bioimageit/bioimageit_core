# -*- coding: utf-8 -*-
"""BioImagePy runner service provider.

This module implement the runner service provider

Classes
------- 
RunnerServiceProvider

"""

from bioimagepy.core.factory import ObjectFactory
from bioimagepy.runners.service_local import LocalRunnerServiceBuilder
from bioimagepy.runners.service_singularity import SingularityRunnerServiceBuilder
from bioimagepy.runners.service_allgo import AllgoRunnerServiceBuilder
from bioimagepy.runners.service_docker import DockerRunnerServiceBuilder


class RunnerServiceProvider(ObjectFactory):
    def get(self, service_id, **kwargs):
        return self.create(service_id, **kwargs)


runnerServices = RunnerServiceProvider()
runnerServices.register_builder('LOCAL', LocalRunnerServiceBuilder())
runnerServices.register_builder('SINGULARITY', SingularityRunnerServiceBuilder())
runnerServices.register_builder('ALLGO', AllgoRunnerServiceBuilder())
runnerServices.register_builder('DOCKER', DockerRunnerServiceBuilder())
