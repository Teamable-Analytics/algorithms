import unittest
from typing import List

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet, PriorityTeam
from api.ai.priority_algorithm.mutations import (
    mutate_local_max_random,
    mutate_local_max,
    mutate_local_max_double_random,
)
from api.ai.priority_algorithm.priority.interfaces import Priority
from tests.test_api.test_ai.test_priority_algorithm.test_mutations._data import (
    EvenPriority,
    JohnPriority,
    get_mock_team_set,
    get_mock_student_dict,
    get_mock_students,
)


class TestMutations(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.priorities: List[Priority] = [EvenPriority()]
        cls.priority_team_set = get_mock_team_set(get_mock_students())
        cls.students = get_mock_students()
        cls.student_dict = get_mock_student_dict(get_mock_students())

    def test_local_max__returns_priority_teams(self):
        priority_team_set = mutate_local_max(
            self.priority_team_set, self.priorities, self.student_dict
        )
        self.assertIsInstance(priority_team_set, PriorityTeamSet)
        for team in priority_team_set.priority_teams:
            self.assertIsInstance(team, PriorityTeam)

    def test_local_max__improves_team_based_on_priority(self):
        score_before = self.priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        priority_team_set = mutate_local_max(
            self.priority_team_set, self.priorities, self.student_dict
        )
        score_after = priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        self.assertGreater(score_after, score_before)

    def test_local_max__improves_team_with_two_priorities(self):
        self.priorities.append(JohnPriority())
        score_before = self.priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        priority_team_set = mutate_local_max(
            self.priority_team_set, self.priorities, self.student_dict
        )
        priority_team_set.score = None
        score_after = priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        self.assertGreater(score_after, score_before)

    def test_mutate_local_max_random__returns_priority_teams(self):
        priority_team_set = mutate_local_max_random(
            self.priority_team_set, self.priorities, self.student_dict
        )
        self.assertIsInstance(priority_team_set, PriorityTeamSet)
        for team in priority_team_set.priority_teams:
            self.assertIsInstance(team, PriorityTeam)

    def test_mutate_local_max_random__improves_score(self):
        self.priorities.append(JohnPriority())
        score_before = self.priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        priority_team_set = mutate_local_max_random(
            self.priority_team_set, self.priorities, self.student_dict
        )
        priority_team_set.score = None
        score_after = priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        self.assertGreater(score_after, score_before)

    def test_mutate_local_max_double_random__returns_priority_teams(self):
        priority_team_set = mutate_local_max_double_random(
            self.priority_team_set, self.priorities, self.student_dict
        )
        self.assertIsInstance(priority_team_set, PriorityTeamSet)
        for team in priority_team_set.priority_teams:
            self.assertIsInstance(team, PriorityTeam)

    def test_mutate_local_max_double_double_random__improves_score(self):
        self.priorities.append(JohnPriority())
        score_before = self.priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        priority_team_set = mutate_local_max_double_random(
            self.priority_team_set, self.priorities, self.student_dict
        )
        priority_team_set.score = None
        score_after = priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        self.assertGreater(score_after, score_before)
