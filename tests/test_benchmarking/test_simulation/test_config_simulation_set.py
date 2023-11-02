import unittest

from api.ai.new.interfaces.algorithm_config import (
    RandomAlgorithmConfig,
    SocialAlgorithmConfig,
    PriorityAlgorithmConfig,
    WeightAlgorithmConfig,
)
from api.models.enums import AlgorithmType
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.simulation.config_simulation_set import ConfigSimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings
from tests.test_benchmarking.test_simulation._data import TestScenario
from utils.validation import is_unique


class TestConfigSimulationSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario = TestScenario()
        cls.student_provider = MockStudentProvider(
            MockStudentProviderSettings(number_of_students=10),
        )

    def test_init__makes_sure_names_are_unique(self):
        base_settings = SimulationSettings(
            num_teams=2,
            scenario=self.scenario,
            student_provider=self.student_provider,
            cache_key="test_cache_key",
        )
        with self.assertRaises(ValueError):
            ConfigSimulationSet(
                settings=base_settings,
                algorithm_set={
                    AlgorithmType.SOCIAL: [
                        SocialAlgorithmConfig(),
                        SocialAlgorithmConfig(name="Name"),
                        SocialAlgorithmConfig(),
                    ]
                },
            )
        with self.assertRaises(ValueError):
            ConfigSimulationSet(
                settings=base_settings,
                algorithm_set={
                    AlgorithmType.RANDOM: [
                        RandomAlgorithmConfig(name="Seth"),
                        RandomAlgorithmConfig(name="Name"),
                        RandomAlgorithmConfig(name="Seth"),
                    ]
                },
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
        simulation_set = ConfigSimulationSet(
            settings=base_settings,
            algorithm_set={AlgorithmType.SOCIAL: [SocialAlgorithmConfig("another")]},
        )
        modified_settings = simulation_set.get_simulation_settings_from_base(
            AlgorithmType.SOCIAL, "another"
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
        weight_configs = [
            WeightAlgorithmConfig("another"),
            WeightAlgorithmConfig("one"),
        ]
        priority_configs = [
            PriorityAlgorithmConfig(),
            PriorityAlgorithmConfig(name="Just Get Good")
        ]
        algorithm_set = {
            AlgorithmType.WEIGHT: weight_configs,
            AlgorithmType.PRIORITY: priority_configs
        }
        simulation_set = ConfigSimulationSet(
            settings=SimulationSettings(
                num_teams=2,
                scenario=self.scenario,
                student_provider=self.student_provider,
                cache_key="test_cache_key",
            ),
            algorithm_set=algorithm_set
        )

        generated_keys = [
            for algorithm in list(algorithm_set.keys()):
                simulation_set.get_simulation_settings_from_base(
                    AlgorithmType.WEIGHT, config.name
                ).cache_key
                for config in algorithm_configs
        ]
        self.assertGreater(len(generated_keys), 0)
        self.assertTrue(is_unique(generated_keys))
