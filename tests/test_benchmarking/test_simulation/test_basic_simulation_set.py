import unittest

from api.dataclasses.enums import AlgorithmType
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.simulation.basic_simulation_set import BasicSimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings
from tests.test_benchmarking.test_simulation._data import TestScenario
from api.utils.validation import is_unique


class TestBasicSimulationSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario = TestScenario()
        cls.student_provider = MockStudentProvider(
            MockStudentProviderSettings(number_of_students=10),
        )

    def test_get_simulation_settings_from_base__preserves_all_other_settings(self):
        # ensures that if more fields are added to the settings class,
        #   then they are updated in this method to ensure preservation
        base_settings = SimulationSettings(
            num_teams=2,
            scenario=self.scenario,
            student_provider=self.student_provider,
            cache_key="test_cache_key",
        )
        simulation_set = BasicSimulationSet(
            settings=base_settings,
        )

        modified_settings = simulation_set.get_simulation_settings_from_base(
            AlgorithmType.RANDOM
        )
        self.assertIsNotNone(base_settings.cache_key)
        for field_name in SimulationSettings.__dataclass_fields__.keys():
            if field_name == "cache_key":  # cache key should be different
                continue
            self.assertEqual(
                modified_settings.__getattribute__(field_name),
                base_settings.__getattribute__(field_name),
            )

    def test_get_simulation_settings_from_base__creates_unique_cache_keys(self):
        simulation_set = BasicSimulationSet(
            settings=SimulationSettings(
                num_teams=2,
                scenario=self.scenario,
                student_provider=self.student_provider,
                cache_key="test_cache_key",
            ),
        )

        generated_keys = [
            simulation_set.get_simulation_settings_from_base(t).cache_key
            for t in AlgorithmType
        ]
        self.assertGreater(len(generated_keys), 0)
        self.assertTrue(is_unique(generated_keys))
