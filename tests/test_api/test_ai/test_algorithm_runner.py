import unittest

from api.ai.algorithm_runner import AlgorithmRunner
from api.models.enums import AlgorithmType


class TestAlgorithmRunner(unittest.TestCase):
    def test_get_algorithm_from_type__all_algorithm_types_must_have_classes(self):
        for algorithm_type in AlgorithmType:
            AlgorithmRunner.get_algorithm_from_type(algorithm_type)
