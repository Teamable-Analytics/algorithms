import copy
import statistics
import time
from collections import defaultdict
from typing import List, Dict, Union

from benchmarking.simulation.mock_algorithm import MockAlgorithm
from api.models.enums import AlgorithmType
from benchmarking.data.interfaces import (
    StudentProvider,
    InitialTeamsProvider,
)
from benchmarking.evaluations.interfaces import Scenario, TeamSetMetric
from benchmarking.simulation.algorithm_translator import AlgorithmTranslator
from old.team_formation.app.team_generator.algorithm.algorithms import AlgorithmOptions

RunOutput = Dict[AlgorithmType, Dict[str, List[float]]]

DEFAULT_ALGORITHM_TYPES = [
    AlgorithmType.RANDOM,
    AlgorithmType.WEIGHT,
    AlgorithmType.SOCIAL,
    AlgorithmType.PRIORITY,
]


class BasicSimulationSet:
    """
    Represents running a Simulation num_runs times and returning the metrics from each of those runs.
    """

    KEY_RUNTIMES = "runtimes"

    def __init__(
        self,
        scenario: Scenario,
        student_provider: StudentProvider,
        metrics: List[TeamSetMetric],
        num_teams: int = None,
        initial_teams_provider: InitialTeamsProvider = None,
        algorithm_types: List[AlgorithmType] = None,
    ):
        self.scenario = scenario
        self.metrics = metrics
        self.student_provider = student_provider

        self.num_teams = num_teams
        self.initial_teams_provider = initial_teams_provider
        self.algorithm_types = algorithm_types or DEFAULT_ALGORITHM_TYPES

        if not self.algorithm_types:
            raise ValueError(
                "If you override algorithm_types, you must specify at least 1 algorithm type to run a simulation."
            )
        if self.num_teams and self.initial_teams_provider:
            raise ValueError(
                "Either specify num_teams OR give a project initial_teams_provider, not both."
            )
        if not self.num_teams and not self.initial_teams_provider:
            raise ValueError(
                "Either num_teams OR a project initial_teams_provider must be specified."
            )
        if not self.metrics:
            raise ValueError("At least one metric must be specified for a simulation.")

        self.run_outputs = defaultdict(dict)
        self.algorithm_options: Dict[AlgorithmType, Union[None, AlgorithmOptions]] = {}
        for algorithm_type in self.algorithm_types:
            self.run_outputs[algorithm_type] = {
                metric.name: [] for metric in self.metrics
            }
            self.run_outputs[algorithm_type].update(
                {BasicSimulationSet.KEY_RUNTIMES: []}
            )

    def run(self, num_runs: int) -> RunOutput:
        initial_teams = (
            self.initial_teams_provider.get() if self.initial_teams_provider else None
        )
        team_generation_options = MockAlgorithm.get_team_generation_options(
            num_students=self.student_provider.num_students,
            num_teams=self.num_teams,
            initial_teams=initial_teams,
        )

        for _ in range(0, num_runs):
            algorithm_students = AlgorithmTranslator.students_to_algorithm_students(
                self.student_provider.get()
            )
            for algorithm_type in self.algorithm_types:
                mock_algorithm = MockAlgorithm(
                    algorithm_type=algorithm_type,
                    team_generation_options=team_generation_options,
                    algorithm_options=self._algorithm_options(algorithm_type),
                )

                start_time = time.time()
                team_set = mock_algorithm.generate(copy.deepcopy(algorithm_students))
                end_time = time.time()

                self.run_outputs[algorithm_type][
                    BasicSimulationSet.KEY_RUNTIMES
                ].append(end_time - start_time)
                for metric in self.metrics:
                    self.run_outputs[algorithm_type][metric.name].append(
                        metric.calculate(team_set)
                    )

        return self.run_outputs

    def _algorithm_options(self, algorithm_type: AlgorithmType):
        if algorithm_type not in self.algorithm_options:
            algorithm_options = MockAlgorithm.algorithm_options_from_scenario(
                algorithm_type=algorithm_type,
                scenario=self.scenario,
                max_project_preferences=self.student_provider.max_project_preferences_per_student,
            )
            self.algorithm_options[algorithm_type] = algorithm_options

        return self.algorithm_options[algorithm_type]

    @staticmethod
    def average_metric(
        run_output: RunOutput, metric_name: str
    ) -> Dict[AlgorithmType, float]:
        averages_output = {}

        for algorithm_type in run_output.keys():
            metric_values = run_output[algorithm_type][metric_name]
            averages_output[algorithm_type] = statistics.mean(metric_values)

        return averages_output
