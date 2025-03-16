from typing import List, Dict

from algorithms.dataclasses.enums import AlgorithmType
from benchmarking.simulation.simulation import SimulationArtifact, Simulation
from benchmarking.simulation.simulation_settings import SimulationSettings

BasicSimulationSetArtifact = Dict[AlgorithmType, SimulationArtifact]


class BasicSimulationSet:
    """
    Represents a set of Simulation runs for when we want to run only 1 of each algorithm
        (as opposed to running 2+ instances of the same algorithm but with different configs)
    """

    DEFAULT_ALGORITHM_TYPES = [
        AlgorithmType.RANDOM,
        AlgorithmType.WEIGHT,
        AlgorithmType.SOCIAL,
        AlgorithmType.PRIORITY,
    ]

    def __init__(
        self,
        settings: SimulationSettings,
        algorithm_types: List[AlgorithmType] = None,
        # todo: it's actually pretty easy to support a custom config for each of the algorithm types passed in
    ):
        self.algorithm_types = algorithm_types or self.DEFAULT_ALGORITHM_TYPES
        if not self.algorithm_types:
            raise ValueError(
                "If you override algorithm_types, you must specify at least 1 algorithm type to run a simulation."
            )
        self.base_settings = settings
        self.base_cache_key = self.base_settings.cache_key
        self.basic_simulation_set_artifact: BasicSimulationSetArtifact = {}

    def run(self, num_runs: int) -> BasicSimulationSetArtifact:
        for algorithm_type in self.algorithm_types:
            # todo: Simulation calculates team gen options and algo options internally, might be wise to not have
            #  that be done N times, but not a huge performance bottleneck currently
            self.basic_simulation_set_artifact[algorithm_type] = Simulation(
                algorithm_type=algorithm_type,
                settings=self.get_simulation_settings_from_base(algorithm_type),
            ).run(num_runs)

        return self.basic_simulation_set_artifact

    def get_simulation_settings_from_base(
        self, algorithm_type: AlgorithmType
    ) -> SimulationSettings:
        cache_key = (
            f"{self.base_settings.cache_key}/{str(algorithm_type)}"
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
        basic_simulation_set_artifact: BasicSimulationSetArtifact,
        algorithm_type: AlgorithmType,
    ) -> SimulationArtifact:
        return basic_simulation_set_artifact.get(algorithm_type, ([], []))
