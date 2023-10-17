import unittest

from api.ai.new.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.models.enums import AlgorithmType
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.simulation.basic_simulation_set_2 import DEFAULT_ALGORITHM_TYPES
from benchmarking.simulation.simulation import Simulation
from benchmarking.simulation.simulation_settings import SimulationSettings
from tests.test_benchmarking.test_simulation._data import TestScenario, TestMetric


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
        cls.settings = SimulationSettings(
            num_teams=2,
            scenario=cls.scenario,
            student_provider=cls.student_provider,
            metrics=[
                cls.metric_1,
                cls.metric_2,
                cls.metric_3,
            ],
        )

    def test_run__outputs_match_given_metrics_and_trials(self):
        simulation_output = Simulation(
            algorithm_type=AlgorithmType.RANDOM,
            settings=self.settings,
        ).run(num_runs=5)

        self.assertEqual(
            len(simulation_output.keys()),
            4,
            msg="Simulation output for {} doesn't include the correct number of keys (3 metrics + 1 runtime)",
        )
        for name in ["Test Metric 1", "Test Metric 2", "Test Metric 3"]:
            self.assertTrue(name in simulation_output)
            self.assertEqual(
                len(simulation_output[name]),
                5,
                msg="Incorrect number of trials for metric.",
            )
        self.assertTrue(Simulation.KEY_RUNTIMES in simulation_output)

    def test_run__works_with_each_algorithm_type(self):
        for algorithm_type in DEFAULT_ALGORITHM_TYPES:
            Simulation(
                algorithm_type=algorithm_type,
                settings=self.settings,
            ).run(num_runs=5)

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
