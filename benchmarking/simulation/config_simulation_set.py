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
        algorithm_type: AlgorithmType,
        algorithm_configs: List[AlgorithmConfig],
    ):
        self.algorithm_type = algorithm_type
        self.base_settings = settings
        self.base_cache_key = self.base_settings.cache_key
        names = [_.name for _ in algorithm_configs]
        if any(item is None for item in names) or not is_unique(names):
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
