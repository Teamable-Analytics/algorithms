import unittest
from unittest.mock import MagicMock

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet, PriorityTeam
from api.ai.priority_algorithm.mutations.local_max import LocalMaxMutation
from api.ai.priority_algorithm.mutations.mutation_set import MutationSet
from api.ai.priority_algorithm.mutations.random_swap import RandomSwapMutation
from api.ai.priority_algorithm.priority_algorithm import (
    create_student_dict,
)
from api.dataclasses.team import TeamShell
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)


class TestMutationSet(unittest.TestCase):
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

    def test_generate_mutations__calls_mutations_correct_number_of_times(self):
        random_mock = MagicMock(return_value=PriorityTeamSet(priority_teams=[]))
        local_mock = MagicMock(return_value=PriorityTeamSet(priority_teams=[]))
        random_swap = RandomSwapMutation()
        random_swap.mutate = random_mock
        local_max = LocalMaxMutation()
        local_max.mutate = local_mock

        mutation_set = MutationSet(
            [
                (random_swap, 7),
                (local_max, 3),
            ]
        )

        mutation_set.generate_mutations(
            self.team_set, [], create_student_dict(self.students)
        )
        self.assertEqual(7, random_swap.mutate.call_count)
        self.assertEqual(3, local_max.mutate.call_count)

    def test_generate_mutations__returns_correct_number_of_mutated_team_sets(self):
        mutation_set = MutationSet(
            [
                (RandomSwapMutation(), 7),
                (LocalMaxMutation(), 3),
            ]
        )

        mutated_team_sets = mutation_set.generate_mutations(
            self.team_set, [], create_student_dict(self.students)
        )
        self.assertEqual(10, len(mutated_team_sets))
