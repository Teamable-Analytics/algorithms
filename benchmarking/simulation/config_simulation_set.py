from typing import List

from api.ai.new.interfaces.algorithm_config import AlgorithmConfig
from api.models.enums import AlgorithmType
from benchmarking.simulation.simulation_settings import SimulationSettings


class ConfigSimulationSet:
    """
    Represents a set of Simulation runs for when you want to run 1 algorithm with multiple configs
    """

    def __init__(self, settings: SimulationSettings, algorithm_type: AlgorithmType,
                 algorithm_configs: List[AlgorithmConfig]):
        self.algorithm_type = algorithm_type
        self.base_settings = settings
        self.base_cache_key = self.base_settings.cache_key
        self.algorithm_configs = algorithm_configs
