import random
import unittest
from typing import List
from collections import Counter

from api.ai.priority_algorithm.custom_models import PriorityTeam, PriorityTeamSet
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.models.team import TeamShell
from api.models.team_set import TeamSet
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from tests.test_api.test_ai.test_priority_algorithm.test_mutations._data import (
    EvenPriority,
    get_mock_team_set,
    get_mock_student_dict,
    get_mock_students_v2,
    JohnPriority,
    LooseEvenPriority,
)
from api.ai.priority_algorithm.mutations.greedy_random_local_max import (
    greedy_local_max_mutation,
)


class TestGreedyRandomLocalMax(unittest.TestCase):
    def setUp(self):
        self.priority_team_set = get_mock_team_set(get_mock_students_v2())
        self.students = get_mock_students_v2()
        self.student_dict = get_mock_student_dict(get_mock_students_v2())

    def test_mutate__changes_team_set(self):
        initial_team_set = self.priority_team_set.clone()
        greedy_local_max_mutation(
            self.priority_team_set,
            [JohnPriority(), LooseEvenPriority()],
            self.student_dict,
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
        for _ in range(10):
            result = greedy_local_max_mutation(
                result,
                priorities,
                student_dict,
            )

        team_sizes = Counter([len(team.student_ids) for team in result.priority_teams])

        self.assertEqual(initial_team_sizes, team_sizes)

    def test_mutate__returns_correct_score(self):
        # 🤌🤌🤌🤌🤌🤌🤌
        priorities = [JohnPriority(), LooseEvenPriority()]
        result = greedy_local_max_mutation(
            self.priority_team_set,
            priorities,
            self.student_dict,
        )
        score = result.calculate_score(priorities, self.student_dict)
        self.assertEqual(score, 624)
