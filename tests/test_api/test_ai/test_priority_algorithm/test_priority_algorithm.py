import unittest
from unittest.mock import MagicMock
from typing import List
from unittest.mock import MagicMock

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.ai.interfaces.algorithm_options import PriorityAlgorithmOptions
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet, PriorityTeam
from api.ai.priority_algorithm.mutations.local_max import LocalMaxMutation
from api.ai.priority_algorithm.mutations.random_swap import RandomSwapMutation
from api.ai.priority_algorithm.priority_algorithm import PriorityAlgorithm
from api.dataclasses.team import TeamShell
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)


class TestPriorityAlgorithm(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        students = MockStudentProvider(
            settings=MockStudentProviderSettings(
                number_of_students=10,
            )
        ).get()
        cls.team_set = PriorityTeamSet(
            priority_teams=[
                PriorityTeam(
                    team_shell=TeamShell(_id=1),
                    student_ids=[_.id for _ in students[0:5]],
                ),
                PriorityTeam(
                    team_shell=TeamShell(_id=2),
                    student_ids=[_.id for _ in students[5:10]],
                ),
            ]
        )
        cls.students = students
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

    def test_generate_mutations__calls_mutations_correct_number_of_times(self):
        random_mock = MagicMock(return_value=PriorityTeamSet(priority_teams=[]))
        local_mock = MagicMock(return_value=PriorityTeamSet(priority_teams=[]))
        random_swap = RandomSwapMutation(7)
        random_swap.mutate_one = random_mock
        local_max = LocalMaxMutation(3)
        local_max.mutate_one = local_mock

        algorithm_config = PriorityAlgorithmConfig(
            MAX_SPREAD=10,
            MAX_TIME=100,
            MAX_ITERATE=1,
            MAX_KEEP=3,
            MUTATIONS=[random_swap, local_max],
        )
        algorithm = PriorityAlgorithm(
            algorithm_options=self.algorithm_options,
            team_generation_options=self.team_generation_options,
            algorithm_config=algorithm_config,
        )

        algorithm.mutate(self.team_set)
        self.assertEqual(7, random_swap.mutate_one.call_count)
        self.assertEqual(3, local_max.mutate_one.call_count)

    def test_generate_mutations__returns_correct_number_of_mutated_team_sets(self):
        mutation_set = [
            RandomSwapMutation(7),
            LocalMaxMutation(3),
        ]
        algorithm_config = PriorityAlgorithmConfig(
            MAX_SPREAD=10,
            MAX_TIME=100,
            MAX_ITERATE=1,
            MAX_KEEP=3,
            MUTATIONS=mutation_set,
        )
        algorithm = PriorityAlgorithm(
            algorithm_options=self.algorithm_options,
            team_generation_options=self.team_generation_options,
            algorithm_config=algorithm_config,
        )

        mutated_team_sets = algorithm.mutate(self.team_set)
        self.assertEqual(10, len(mutated_team_sets))

    def test_mutate__returns_correct_type(self):
        mutation_set = [
            RandomSwapMutation(7),
            LocalMaxMutation(3),
        ]
        algorithm_config = PriorityAlgorithmConfig(
            MAX_SPREAD=10,
            MAX_TIME=100,
            MAX_ITERATE=1,
            MAX_KEEP=3,
            MUTATIONS=mutation_set,
        )
        algorithm = PriorityAlgorithm(
            algorithm_options=self.algorithm_options,
            team_generation_options=self.team_generation_options,
            algorithm_config=algorithm_config,
        )
        mutated_team_sets = algorithm.mutate(self.team_set)
        self.assertIsInstance(mutated_team_sets, List)
        self.assertIsInstance(mutated_team_sets[0], PriorityTeamSet)
