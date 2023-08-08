import copy
import statistics
import time
from collections import defaultdict
from typing import List, Dict, Tuple, Union

from restructure.algorithms.mock_algorithm import MockAlgorithm
from restructure.models.enums import AlgorithmType
from restructure.models.student import Student
from restructure.simulations.data.interfaces import (
    StudentProvider,
    InitialTeamsProvider,
)
from restructure.simulations.evaluations.interfaces import Scenario, TeamSetMetric
from restructure.simulations.util.algorithm_translator import AlgorithmTranslator
from team_formation.app.team_generator.algorithm.algorithms import AlgorithmOptions

RunOutput = Dict[AlgorithmType, Dict[str, List[float]]]


class Simulation:
    """
    todo: Makes the Y-value(s)
    Represents running a SimulationInstance num_runs times and returning the metrics from each of those runs.
    """

    KEY_METRIC_VALUES = "metric_values"
    KEY_RUNTIMES = "runtimes"

    def __init__(
        self,
        scenario: Scenario,
        student_provider: StudentProvider,
        metric: TeamSetMetric,
        num_teams: int = None,
        initial_teams_provider: InitialTeamsProvider = None,
    ):
        self.scenario = scenario
        self.metric = metric
        self.student_provider = student_provider

        self.num_teams = num_teams
        self.initial_teams_provider = initial_teams_provider

        if self.num_teams and self.initial_teams_provider:
            raise ValueError(
                "Either specify num_teams OR give a project initial_teams_provider, not both."
            )
        if not self.num_teams and not self.initial_teams_provider:
            raise ValueError(
                "Either num_teams OR a project initial_teams_provider must be specified."
            )

        self.run_outputs = defaultdict(dict)
        self.algorithm_options: Dict[AlgorithmType, Union[None, AlgorithmOptions]] = {}
        for algorithm_type in AlgorithmType:
            self.algorithm_options[algorithm_type] = None
            self.run_outputs[algorithm_type] = {
                Simulation.KEY_METRIC_VALUES: [],
                Simulation.KEY_RUNTIMES: [],
            }

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
            for algorithm_type in AlgorithmType:
                mock_algorithm = MockAlgorithm(
                    algorithm_type=algorithm_type,
                    team_generation_options=team_generation_options,
                    algorithm_options=self._algorithm_options(algorithm_type),
                )

                start_time = time.time()
                team_set = mock_algorithm.generate(copy.deepcopy(algorithm_students))
                end_time = time.time()

                self.run_outputs[algorithm_type][Simulation.KEY_RUNTIMES].append(
                    end_time - start_time
                )
                self.run_outputs[algorithm_type][Simulation.KEY_METRIC_VALUES].append(
                    self.metric.calculate(team_set)
                )

        return self.run_outputs

    def _algorithm_options(self, algorithm_type: AlgorithmType):
        if self.algorithm_options[algorithm_type] is None:
            algorithm_options = MockAlgorithm.algorithm_options_from_scenario(
                algorithm_type=algorithm_type,
                scenario=self.scenario,
                max_project_preferences=self.student_provider.max_project_preferences_per_student,
            )
            self.algorithm_options[algorithm_type] = algorithm_options

        return self.algorithm_options[algorithm_type]

    @staticmethod
    def average_metric(run_output: RunOutput) -> Dict[AlgorithmType, float]:
        averages_output = {}

        for algorithm_type in AlgorithmType:
            metric_values = run_output[algorithm_type][Simulation.KEY_METRIC_VALUES]
            averages_output[algorithm_type] = statistics.mean(metric_values)

        return averages_output
