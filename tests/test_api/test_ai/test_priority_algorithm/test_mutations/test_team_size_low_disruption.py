import unittest

from algorithms.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet, PriorityTeam
from algorithms.ai.priority_algorithm.mutations.team_size_low_disruption import (
    get_sizes,
    TeamSizeLowDisruptionMutation,
)
from algorithms.dataclasses.team import TeamShell
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.simulation.mock_algorithm import MockAlgorithm
from tests.test_api.test_ai.test_priority_algorithm.test_mutations._data import (
    get_mock_student_dict,
)


class TestTeamSizeLowDisruptionMutation(unittest.TestCase):
    def setUp(self):
        students = MockStudentProvider(
            settings=MockStudentProviderSettings(
                number_of_students=50,
            )
        ).get()
        self.student_dict = get_mock_student_dict(students)
        student_ids = list(self.student_dict.keys())
        self.team_set = PriorityTeamSet(
            priority_teams=[
                PriorityTeam(
                    student_ids=student_ids[i : i + 5], team_shell=TeamShell(i)
                )
                for i in range(10)
            ]
        )
        self.students = students
        self.mutation = TeamSizeLowDisruptionMutation()
        self.team_generation_options = MockAlgorithm.get_team_generation_options(
            num_students=50, num_teams=10, min_team_size=3, max_team_size=7
        )

    def test_get_sizes__sums_to_num_students(self):
        sizes = get_sizes(100, 500, 3, 6)
        self.assertEqual(500, sum(sizes))

    def test_get_sizes__sizes_are_in_range(self):
        sizes = get_sizes(100, 500, 3, 6)
        for size in sizes:
            self.assertLessEqual(size, 6)
            self.assertGreaterEqual(size, 3)

    def test_get_sizes__len_sizes_equals_num_teams(self):
        sizes = get_sizes(100, 500, 3, 6)
        self.assertEqual(100, len(sizes))

    def test_mutate_one__returns_correct_type(self):
        mutated_team_set = self.mutation.mutate_one(
            self.team_set.clone(),
            [],
            self.student_dict,
            self.team_generation_options,
        )
        self.assertIsInstance(mutated_team_set, PriorityTeamSet)

    def test_mutate_one__returns_all_students(self):
        mutated_team_set = self.mutation.mutate_one(
            self.team_set.clone(),
            [],
            self.student_dict,
            self.team_generation_options,
        )
        original_students = [
            student
            for team in self.team_set.priority_teams
            for student in team.student_ids
        ]
        returned_students = [
            student
            for team in mutated_team_set.priority_teams
            for student in team.student_ids
        ]
        self.assertEqual(len(self.students), len(returned_students))
        self.assertEqual(set(original_students), set(returned_students))

    def test_mutate_one__team_sizes_are_in_bounds(self):
        mutated_team_set = self.mutation.mutate_one(
            self.team_set.clone(),
            [],
            self.student_dict,
            self.team_generation_options,
        )
        for team in mutated_team_set.priority_teams:
            self.assertLessEqual(
                len(team.student_ids), self.team_generation_options.max_team_size
            )
            self.assertGreaterEqual(
                len(team.student_ids), self.team_generation_options.min_team_size
            )

    def test_mutate_one__at_most_N_teams_are_changed(self):
        mutated_team_set = TeamSizeLowDisruptionMutation(num_teams=4).mutate_one(
            self.team_set.clone(),
            [],
            self.student_dict,
            self.team_generation_options,
        )
        num_changed = 0
        for mutated_team in mutated_team_set.priority_teams:
            before = [
                _
                for _ in self.team_set.priority_teams
                if _.team_shell.id == mutated_team.team_shell.id
            ][0]
            if set(before.student_ids) != set(mutated_team.student_ids):
                num_changed += 1
        self.assertLessEqual(num_changed, 4)
