import unittest

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet, PriorityTeam
from api.ai.priority_algorithm.mutations.random_team_size_change import (
    RandomTeamSizeMutation,
)
from api.dataclasses.team import TeamShell
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.simulation.mock_algorithm import MockAlgorithm


class TestRandomSlice(unittest.TestCase):
    def test_mutate__produces_team_sizes_in_bounds(self):
        students = MockStudentProvider(
            settings=MockStudentProviderSettings(
                number_of_students=100,
            )
        ).get()
        team_set = PriorityTeamSet(
            priority_teams=[
                PriorityTeam(
                    student_ids=[
                        student.id
                        for student in students[team_id * 5 : team_id * 5 + 5]
                    ],
                    team_shell=TeamShell(team_id),
                )
                for team_id in range(20)
            ]
        )
        random_team_size_mutation = RandomTeamSizeMutation()
        random_team_size_mutation.mutate_one(
            team_set,
            [],
            {},
            MockAlgorithm.get_team_generation_options(
                num_students=100, num_teams=20, min_team_size=3, max_team_size=7
            ),
        )
        after_students = []
        for team in team_set.priority_teams:
            team_size = len(team.student_ids)
            self.assertGreaterEqual(team_size, 3)
            self.assertLessEqual(team_size, 7)
            for student in team.student_ids:
                after_students.append(student)
        self.assertEqual(len(after_students), 100)
