import unittest

from algorithms.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet, PriorityTeam
from algorithms.ai.priority_algorithm.mutations.random_slice import RandomSliceMutation
from algorithms.dataclasses.team import TeamShell
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.simulation.mock_algorithm import MockAlgorithm


class TestRandomSlice(unittest.TestCase):
    def test_mutate__changes_one_student_in_each_team_set(self):
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
        initial_team_set = team_set.clone()
        random_slice_mutation = RandomSliceMutation()
        random_slice_mutation.mutate_one(
            team_set,
            [],
            {},
            MockAlgorithm.get_team_generation_options(
                num_students=10, num_teams=2, min_team_size=1, max_team_size=10
            ),
        )

        num_teams_changed = 0
        for initial_team, mutated_team in zip(
            initial_team_set.priority_teams, team_set.priority_teams
        ):
            self.assertEqual(initial_team.team_shell.id, mutated_team.team_shell.id)

            self.assertEqual(
                len(initial_team.student_ids), len(mutated_team.student_ids)
            )

            # Check that the teams are different,
            # but there is a chance that a student gets put back on the same team

            # Gives the new student(s) in the mutated team
            diff = list(set(mutated_team.student_ids) - set(initial_team.student_ids))
            num_students_changed = len(diff)
            num_teams_changed += 1 if num_students_changed > 0 else 0
            self.assertTrue(num_students_changed in [0, 1])

        # Technically flaky, but it's a 1 in 104,857,600,000,000,000,000,000,000 chance to fail
        self.assertGreater(num_teams_changed, 0)
