import unittest

from api.models.enums import AlgorithmType
from api.models.project import Project
from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProvider,
    MockInitialTeamsProviderSettings,
)
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation import Simulation
from benchmarking.simulation.simulation_settings import SimulationSettings
from tests.test_benchmarking.test_simulation._data import TestScenario, TestMetric


class TestRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario = TestScenario()
        cls.student_provider = MockStudentProvider(
            MockStudentProviderSettings(number_of_students=10),
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
        cls.metrics = [TestMetric(name="A"), TestMetric(name="B")]

    def test_run__works_without_errors(self):
        team_sets, run_times = Simulation(
            algorithm_type=AlgorithmType.RANDOM,
            settings=self.complex_settings,
        ).run(num_runs=1)

        Insight(
            team_sets=team_sets,
            run_times=run_times,
            metrics=self.metrics,
        ).generate()
