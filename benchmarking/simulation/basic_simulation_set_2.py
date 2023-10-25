from typing import List, Dict

from api.models.enums import AlgorithmType
from benchmarking.simulation.simulation import SimulationArtifact, Simulation
from benchmarking.simulation.simulation_settings import SimulationSettings

BasicSimulationSetArtifact = Dict[AlgorithmType, SimulationArtifact]


class BasicSimulationSet2:
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
        self.basic_simulation_set_artifact: BasicSimulationSetArtifact = {}

    def run(self, num_runs: int) -> BasicSimulationSetArtifact:
        for algorithm_type in self.algorithm_types:
            self.basic_simulation_set_artifact[algorithm_type] = Simulation(
                algorithm_type=algorithm_type,
                settings=self.base_settings,
            ).run(num_runs)

        return self.basic_simulation_set_artifact

    @staticmethod
    def get_artifact(
        basic_simulation_set_artifact: BasicSimulationSetArtifact,
        algorithm_type: AlgorithmType,
    ) -> SimulationArtifact:
        return basic_simulation_set_artifact.get(algorithm_type, ([], []))
