import random
import unittest
from collections import Counter

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeam, PriorityTeamSet
from api.ai.priority_algorithm.mutations.greedy_local_max import GreedyLocalMaxMutation
from api.dataclasses.team import TeamShell
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.simulation.mock_algorithm import MockAlgorithm
from tests.test_api.test_ai.test_priority_algorithm.test_mutations._data import (
    get_mock_team_set,
    get_mock_student_dict,
    get_mock_students_v2,
    JohnPriority,
    LooseEvenPriority,
)


class TestGreedyRandomLocalMax(unittest.TestCase):
    def setUp(self):
        self.priority_team_set = get_mock_team_set(get_mock_students_v2())
        self.students = get_mock_students_v2()
        self.student_dict = get_mock_student_dict(get_mock_students_v2())

    def test_mutate__changes_team_set(self):
        initial_team_set = self.priority_team_set.clone()
        greedy_local_max = GreedyLocalMaxMutation()
        greedy_local_max.mutate_one(
            self.priority_team_set,
            [JohnPriority(), LooseEvenPriority()],
            self.student_dict,
            MockAlgorithm.get_team_generation_options(
                num_students=10, num_teams=2, min_team_size=1, max_team_size=10
            ),
        )

        self.assertNotEqual(
            initial_team_set.priority_teams[0].student_ids,
            self.priority_team_set.priority_teams[0].student_ids,
        )
        self.assertNotEqual(
            initial_team_set.priority_teams[1].student_ids,
            self.priority_team_set.priority_teams[1].student_ids,
        )

    def test_mutate__returns_correct_sized_teams(self):
        priorities = [JohnPriority(), LooseEvenPriority()]

        # Make more juicy team sizes
        mock_students = MockStudentProvider(
            settings=MockStudentProviderSettings(
                number_of_students=50,
            )
        ).get()
        student_dict = get_mock_student_dict(mock_students)
        teams = []
        for i in range(10):
            teams.append(
                PriorityTeam(
                    team_shell=TeamShell(i), student_ids=[mock_students.pop(i).id]
                )
            )
        for student in mock_students:
            num = random.randrange(10)
            teams[num].student_ids.append(student.id)

        initial_team_sizes = Counter([len(team.student_ids) for team in teams])
        result = PriorityTeamSet(
            priority_teams=teams,
        )
        greedy_local_max = GreedyLocalMaxMutation()
        for _ in range(10):
            result = greedy_local_max.mutate_one(
                result,
                priorities,
                student_dict,
                MockAlgorithm.get_team_generation_options(
                    num_students=10, num_teams=2, min_team_size=1, max_team_size=10
                ),
            )

        team_sizes = Counter([len(team.student_ids) for team in result.priority_teams])

        self.assertEqual(initial_team_sizes, team_sizes)

    def test_mutate__returns_correct_score(self):
        # 🤌🤌🤌🤌🤌🤌🤌
        priorities = [JohnPriority(), LooseEvenPriority()]
        greedy_local_max = GreedyLocalMaxMutation()
        result = greedy_local_max.mutate_one(
            self.priority_team_set,
            priorities,
            self.student_dict,
            MockAlgorithm.get_team_generation_options(
                num_students=10, num_teams=2, min_team_size=1, max_team_size=10
            ),
        )
        score = result.calculate_score(priorities, self.student_dict)
        self.assertEqual(score, 624)
