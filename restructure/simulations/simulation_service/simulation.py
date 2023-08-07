import copy
import time
from typing import List, Dict, Tuple

from restructure.algorithms.main import MockAlgorithm
from restructure.models.enums import AlgorithmType
from restructure.models.student import Student
from restructure.simulations.data_service.interfaces import (
    StudentProvider,
    InitialTeamsProvider,
)
from restructure.simulations.evaluations.interfaces import Scenario, TeamSetMetric
from restructure.simulations.util.converter import Converter


class Simulation:
    """
    todo: Makes the Y-value(s)
    Represents running a SimulationInstance num_runs times and returning the metrics from each of those runs.
    """

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

        self.students: List[Student] = self.student_provider.get()

    def run(self, num_runs: int) -> Dict[AlgorithmType, Tuple[List[float]]]:
        """
        Returns a dictionary mapping each algorithm to => Tuple(
            list of the output of the metric you are calculating for,
            a list of the runtimes for each run of that algorithm
        )
        """
        outputs = {algorithm: [] for algorithm in AlgorithmType}
        initial_teams = (
            self.initial_teams_provider.get() if self.initial_teams_provider else None
        )
        algorithm_students = Converter.students_to_algorithm_students(self.students)

        for algorithm_type in AlgorithmType:
            metric_logs = []
            runtime_logs = []

            mock_algorithm = MockAlgorithm(
                algorithm_type=algorithm_type,
                team_generation_options=MockAlgorithm.get_team_generation_options(
                    num_students=len(self.students),
                    num_teams=self.num_teams,
                    initial_teams=initial_teams,
                ),
                algorithm_options=MockAlgorithm.algorithm_options_from_scenario(
                    algorithm_type=algorithm_type,
                    scenario=self.scenario,
                    max_project_preferences=self.student_provider.max_project_preferences_per_student,
                ),
            )

            for _ in range(0, num_runs):
                start_time = time.time()
                team_set = mock_algorithm.generate(copy.deepcopy(algorithm_students))
                end_time = time.time()

                runtime_logs.append(end_time - start_time)
                metric_logs.append(self.metric.calculate(team_set))

            outputs[algorithm_type] = metric_logs, runtime_logs

        return outputs
