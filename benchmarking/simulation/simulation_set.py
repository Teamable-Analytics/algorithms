from typing import List, Dict

import numpy as np

from api.ai.interfaces.algorithm_config import AlgorithmConfig
from api.models.enums import AlgorithmType
from benchmarking.simulation.simulation import SimulationArtifact, Simulation
from benchmarking.simulation.simulation_settings import SimulationSettings
from utils.validation import is_unique

SimulationSetArtifact = Dict[str, SimulationArtifact]


class SimulationSet:
    """
    Represents a set of Simulation runs for when you want to run algorithms with config files
    """

    def __init__(
        self,
        settings: SimulationSettings,
        algorithm_set: Dict[AlgorithmType, List[AlgorithmConfig]],
    ):
        self.algorithm_set = algorithm_set
        self.base_settings = settings
        self.base_cache_key = self.base_settings.cache_key
        self.algorithm_types = list(algorithm_set.keys())
        # Need to check that default is not specified, and that all names are unique
        for configs in algorithm_set.values():
            names = [_.name for _ in configs]
            if not is_unique(names):
                raise ValueError("For each algorithm, the config names must be unique!")
        self.basic_simulation_set_artifact: SimulationSetArtifact = {}

    def run(self, num_runs: int) -> SimulationSetArtifact:
        # Generate `num_runs` seeds
        seeds = _get_seeds(num_runs, self.base_cache_key)

        for algorithm in self.algorithm_types:
            for config in self.algorithm_set[algorithm]:
                print(f"Running {str(algorithm)}-{config.name}")
                self.basic_simulation_set_artifact[
                    f"{str(algorithm)}-{config.name}"
                ] = Simulation(
                    algorithm_type=algorithm,
                    settings=self.get_simulation_settings_from_base(
                        algorithm, name=config.name
                    ),
                    config=config,
                ).run(
                    num_runs,
                    seeds,
                )

        return self.basic_simulation_set_artifact

    def get_simulation_settings_from_base(
        self, algorithm_type: AlgorithmType, name: str
    ) -> SimulationSettings:
        cache_key = (
            f"{self.base_settings.cache_key}/{str(algorithm_type)}-{name}"
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
        config_simulation_set_artifact: SimulationSetArtifact,
        name: str,
    ) -> SimulationArtifact:
        return config_simulation_set_artifact.get(name, ([], []))


def _get_seeds(num_seeds: int, cache_key: str) -> List[int]:
    seed_generator_seed = abs(hash(cache_key)) if cache_key else None
    rng = np.random.default_rng(seed_generator_seed)
    return [
        # Arbitrary upper bound. Big number, so we have lower chance of duplicate seed.
        int(rng.integers(0, 1_000_000_000))
        for _ in range(num_seeds)
    ]
