import unittest
from unittest import mock

import api.ai.priority_algorithm.mutations  # done this way to mutation functions can be mocked properly
from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.ai.interfaces.algorithm_options import PriorityAlgorithmOptions
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.ai.priority_algorithm.priority_algorithm import PriorityAlgorithm
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)


class TestPriorityAlgorithm(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.algorithm_options = PriorityAlgorithmOptions(
            priorities=[],
            max_project_preferences=0,
        )
        cls.team_generation_options = TeamGenerationOptions(
            max_team_size=5,
            min_team_size=4,
            total_teams=2,
            initial_teams=[],
        )

    @mock.patch(
        "api.ai.priority_algorithm.mutations.mutate_random_swap", return_value=[]
    )
    @mock.patch("api.ai.priority_algorithm.mutations.mutate_local_max", return_value=[])
    def test_mutate__uses_mutation_functions_from_config(
        self, mock_local_max, mock_random_swap
    ):
        algorithm_config = PriorityAlgorithmConfig(
            MAX_SPREAD=10,
            MAX_TIME=100,
            MAX_ITERATE=1,
            MAX_KEEP=3,
            MUTATIONS=[
                (api.ai.priority_algorithm.mutations.mutate_random_swap, 7),
                (api.ai.priority_algorithm.mutations.mutate_local_max, 3),
            ],
        )
        algorithm = PriorityAlgorithm(
            algorithm_options=self.algorithm_options,
            team_generation_options=self.team_generation_options,
            algorithm_config=algorithm_config,
        )

        test_team_set = algorithm.generate_initial_team_set(
            MockStudentProvider(
                settings=MockStudentProviderSettings(
                    number_of_students=10,
                )
            ).get()
        )

        algorithm.mutate(test_team_set)
        self.assertEqual(mock_random_swap.call_count, 7)
        self.assertEqual(mock_local_max.call_count, 3)

    def test_mutate__returns_correct_number_of_mutated_team_sets(self):
        algorithm_config = PriorityAlgorithmConfig(
            MAX_SPREAD=10,
            MAX_TIME=100,
            MAX_ITERATE=1,
            MAX_KEEP=3,
        )
        algorithm = PriorityAlgorithm(
            algorithm_options=self.algorithm_options,
            team_generation_options=self.team_generation_options,
            algorithm_config=algorithm_config,
        )

        test_team_set = algorithm.generate_initial_team_set(
            MockStudentProvider(
                settings=MockStudentProviderSettings(
                    number_of_students=10,
                )
            ).get()
        )

        mutated_team_sets = algorithm.mutate(test_team_set)
        self.assertEqual(len(mutated_team_sets), algorithm_config.MAX_SPREAD)
