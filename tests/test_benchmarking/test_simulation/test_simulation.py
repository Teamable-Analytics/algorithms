import unittest
from typing import List

from benchmarking.data.interfaces import MockStudentProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProvider
from benchmarking.evaluations.goals import DiversityGoal
from benchmarking.evaluations.interfaces import TeamSetMetric, Scenario
from benchmarking.simulation.simulation import Simulation
from models.enums import DiversifyType, AlgorithmType


class TestMetric(TeamSetMetric):
    def calculate(self, team_set: "TeamSet") -> float:
        return 1


class TestScenario(Scenario):
    @property
    def name(self) -> str:
        return "Test Scenario"

    @property
    def goals(self) -> List["Goal"]:
        return [
            DiversityGoal(
                strategy=DiversifyType.DIVERSIFY,
                attribute=1,
            )
        ]


class TestSimulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario = TestScenario()
        cls.metric_1 = TestMetric(name="Test Metric 1")
        cls.metric_2 = TestMetric(name="Test Metric 2")
        cls.metric_3 = TestMetric(name="Test Metric 3")
        cls.student_provider = MockStudentProvider(
            MockStudentProviderSettings(number_of_students=10)
        )

    def test_run__run_outputs_match_given_metrics_and_trials(self):
        simulation = Simulation(
            num_teams=2,
            scenario=self.scenario,
            student_provider=self.student_provider,
            metrics=[
                self.metric_1,
                self.metric_2,
                self.metric_3,
            ],
        )

        simulation_outputs = simulation.run(num_runs=5)

        for algo_type in simulation.algorithm_types:
            run_output = simulation_outputs[algo_type]
            self.assertEqual(
                len(run_output.keys()),
                4,
                msg="Run output for {} doesn't include the correct number of keys (3 metrics + 1 runtime)",
            )
            for name in ["Test Metric 1", "Test Metric 2", "Test Metric 3"]:
                self.assertTrue(name in run_output)
                self.assertEqual(len(run_output[name]), 5)
            self.assertTrue(Simulation.KEY_RUNTIMES in run_output)
