import copy
import time
from typing import List, Tuple

from api.ai.algorithm_runner import AlgorithmRunner
from api.ai.new.interfaces.algorithm_config import AlgorithmConfig
from api.models.enums import AlgorithmType
from api.models.team_set import TeamSet
from benchmarking.simulation.mock_algorithm_2 import MockAlgorithm2
from benchmarking.simulation.simulation_settings import SimulationSettings

# list of floats tracks the runtime of each run
SimulationArtifact = Tuple[List[TeamSet], List[float]]


class Simulation:
    """
    Represents running a Simulation num_runs times and returning the team sets from each of those runs.
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
        self.run_times = []
        self.team_sets = []

    def run(self, num_runs: int) -> SimulationArtifact:
        custom_initial_teams = (
            self.settings.initial_teams_provider.get()
            if self.settings.initial_teams_provider
            else None
        )
        team_generation_options = MockAlgorithm2.get_team_generation_options(
            num_students=self.settings.student_provider.num_students,
            num_teams=self.settings.num_teams,
            initial_teams=custom_initial_teams,
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

            self.run_times.append(end_time - start_time)
            self.team_sets.append(team_set)

        return self.team_sets, self.run_times
