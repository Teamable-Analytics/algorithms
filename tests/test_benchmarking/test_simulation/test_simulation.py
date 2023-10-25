import unittest

from api.ai.new.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.models.enums import AlgorithmType
from api.models.project import Project
from api.models.team_set import TeamSet
from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProvider,
    MockInitialTeamsProviderSettings,
)
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.simulation.basic_simulation_set_2 import BasicSimulationSet2
from benchmarking.simulation.simulation import Simulation
from benchmarking.simulation.simulation_settings import SimulationSettings
from tests.test_benchmarking.test_simulation._data import TestScenario, TestMetric


class TestSimulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario = TestScenario()
        cls.student_provider = MockStudentProvider(
            MockStudentProviderSettings(number_of_students=10),
        )
        cls.settings = SimulationSettings(
            num_teams=2,
            scenario=cls.scenario,
            student_provider=cls.student_provider,
        )

        cls.student_provider_with_preferences = MockStudentProvider(
            MockStudentProviderSettings(
                number_of_students=10,
                project_preference_options=[1, 2],
                num_project_preferences_per_student=2,
            ),
        )
        cls.initial_teams_provider = MockInitialTeamsProvider(
            MockInitialTeamsProviderSettings(
                projects=[
                    Project(_id=1),
                    Project(_id=2),
                ]
            )
        )
        cls.complex_settings = SimulationSettings(
            scenario=cls.scenario,
            student_provider=cls.student_provider_with_preferences,
            initial_teams_provider=cls.initial_teams_provider,
        )

    def test_run__outputs_match_given_trials_and_schema(self):
        team_sets, run_times = Simulation(
            algorithm_type=AlgorithmType.RANDOM,
            settings=self.settings,
        ).run(num_runs=5)

        self.assertEqual(len(team_sets), 5)
        self.assertEqual(len(run_times), 5)
        # redundant but left in as a safeguard for future logic changes
        self.assertEqual(len(team_sets), len(run_times))

        for team_set in team_sets:
            self.assertIsInstance(team_set, TeamSet)
        for run_time in run_times:
            self.assertIsInstance(run_time, float)

    def test_run__works_with_each_algorithm_type(self):
        for algorithm_type in BasicSimulationSet2.DEFAULT_ALGORITHM_TYPES:
            Simulation(
                algorithm_type=algorithm_type,
                settings=self.settings,
            ).run(num_runs=1)

    def test_run__works_with_complex_settings(self):
        for algorithm_type in BasicSimulationSet2.DEFAULT_ALGORITHM_TYPES:
            Simulation(
                algorithm_type=algorithm_type,
                settings=self.complex_settings,
            ).run(num_runs=1)

    def test_run__works_with_configs(self):
        # fixme: should eventually test that the custom config passed
        #  is actually used, for now just tests that it doesn't break
        Simulation(
            algorithm_type=AlgorithmType.PRIORITY,
            config=PriorityAlgorithmConfig(
                MAX_KEEP=1,
                MAX_SPREAD=1,
                MAX_TIME=1,
                MAX_ITERATE=2222,
            ),
            settings=self.settings,
        ).run(num_runs=1)
