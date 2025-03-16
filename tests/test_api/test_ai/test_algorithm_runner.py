import unittest

from algorithms.ai.algorithm_runner import AlgorithmRunner
from algorithms.dataclasses.enums import AlgorithmType


class TestAlgorithmRunner(unittest.TestCase):
    def test_get_algorithm_from_type__all_algorithm_types_must_have_classes(self):
        for algorithm_type in AlgorithmType:
            AlgorithmRunner.get_algorithm_from_type(algorithm_type)

    def test_get_algorithm_options_class__all_algorithm_types_must_have_classes(self):
        for algorithm_type in AlgorithmType:
            AlgorithmRunner.get_algorithm_option_class(algorithm_type)

    def test_get_algorithm_config_class__all_algorithm_types_must_have_classes(self):
        for algorithm_type in AlgorithmType:
            AlgorithmRunner.get_algorithm_config_class(algorithm_type)
