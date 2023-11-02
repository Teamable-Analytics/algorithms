from typing import List, Dict

from api.ai.new.interfaces.algorithm_config import AlgorithmConfig
from api.models.enums import AlgorithmType
from benchmarking.simulation.simulation import SimulationArtifact, Simulation
from benchmarking.simulation.simulation_settings import SimulationSettings
from utils.validation import is_unique

ConfigSimulationSetArtifact = Dict[str, SimulationArtifact]


class ConfigSimulationSet:
    """
    Represents a set of Simulation runs for when you want to run 1 algorithm with multiple configs
    """

    def __init__(
        self,
        settings: SimulationSettings,
        algorithm_types: List[AlgorithmType],
        algorithm_configs: Dict[AlgorithmType, List[AlgorithmConfig]],
    ):
        if not is_unique(algorithm_types):
            raise ValueError("Each algorithm can only be specified once")
        self.algorithm_type = algorithm_types
        self.base_settings = settings
        self.base_cache_key = self.base_settings.cache_key
        # Need to check that default is not specified, and that all names are unique
        for configs in algorithm_configs.values():
            names = [_.name for _ in configs]
            if [item.lower() for item in names].count("default") > 0:
                raise ValueError("Default is a reserved name for algorithm configs.")
            if len([item for item in names if item is None]) > 1:
                raise ValueError("Only one config can use the default")
            if not is_unique(names):
                raise ValueError("Each algorithm config must have a unique name")
        self.algorithm_configs = algorithm_configs
        self.basic_simulation_set_artifact: ConfigSimulationSetArtifact = {}

    def run(self, num_runs: int) -> ConfigSimulationSetArtifact:
        for config in self.algorithm_configs:
            self.basic_simulation_set_artifact[config.name] = Simulation(
                algorithm_type=self.algorithm_type,
                settings=self.get_simulation_settings_from_base(name=config.name),
                config=config,
            ).run(num_runs)

        return self.basic_simulation_set_artifact

    def get_simulation_settings_from_base(self, name: str) -> SimulationSettings:
        cache_key = (
            f"{self.base_settings.cache_key}/{name}"
            if self.base_settings.cache_key
            else None
        )
        return SimulationSettings(
            scenario=self.base_settings.scenario,
            student_provider=self.base_settings.student_provider,
            initial_teams_provider=self.base_settings.initial_teams_provider,
            num_teams=self.base_settings.num_teams,
            cache_key=cache_key,
        )

    @staticmethod
    def get_artifact(
        config_simulation_set_artifact: ConfigSimulationSetArtifact,
        name: str,
    ) -> SimulationArtifact:
        return config_simulation_set_artifact.get(name, ([], []))
