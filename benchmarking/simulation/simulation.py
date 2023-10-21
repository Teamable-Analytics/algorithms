import copy
import statistics
import time
from collections import defaultdict
from typing import List, Dict

from api.ai.algorithm_runner import AlgorithmRunner
from api.ai.new.interfaces.algorithm_config import AlgorithmConfig
from api.models.enums import AlgorithmType
from benchmarking.simulation.mock_algorithm_2 import MockAlgorithm2
from benchmarking.simulation.simulation_settings import SimulationSettings

SimulationOutput = Dict[str, List[float]]


class Simulation:
    """
    Represents running a Simulation num_runs times and returning the metrics from each of those runs.
    """

    KEY_RUNTIMES = "runtimes"

    def __init__(
        self,
        algorithm_type: AlgorithmType,
        settings: SimulationSettings,
        config: AlgorithmConfig = None,
    ):
        self.algorithm_type = algorithm_type
        self.settings = settings
        self.config = config
        self.run_outputs = defaultdict(dict)
        self.simulation_outputs = {metric.name: [] for metric in self.settings.metrics}
        self.simulation_outputs.update({Simulation.KEY_RUNTIMES: []})

    def run(self, num_runs: int) -> SimulationOutput:
        initial_teams = (
            self.settings.initial_teams_provider.get()
            if self.settings.initial_teams_provider
            else None
        )
        team_generation_options = MockAlgorithm2.get_team_generation_options(
            num_students=self.settings.student_provider.num_students,
            num_teams=self.settings.num_teams,
            initial_teams=initial_teams,
        )

        algorithm_options = MockAlgorithm2.algorithm_options_from_scenario(
            algorithm_type=self.algorithm_type,
            scenario=self.settings.scenario,
            max_project_preferences=self.settings.student_provider.max_project_preferences_per_student,
        )

        runner = AlgorithmRunner(
            algorithm_type=self.algorithm_type,
            team_generation_options=team_generation_options,
            algorithm_options=algorithm_options,
            algorithm_config=self.config,
        )

        for _ in range(0, num_runs):
            students = self.settings.student_provider.get()

            start_time = time.time()
            team_set = runner.generate(copy.deepcopy(students))
            end_time = time.time()

            self.simulation_outputs[Simulation.KEY_RUNTIMES].append(
                end_time - start_time
            )
            for metric in self.settings.metrics:
                self.simulation_outputs[metric.name].append(metric.calculate(team_set))

        return self.simulation_outputs

    @staticmethod
    def average_metric(simulation_output: SimulationOutput, metric_name: str) -> float:
        metric_values = simulation_output[metric_name]
        return statistics.mean(metric_values)
