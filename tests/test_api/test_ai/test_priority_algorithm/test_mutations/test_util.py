import unittest
from typing import List

from api.ai.priority_algorithm.interfaces import Priority
from api.ai.priority_algorithm.mutations.utils import score
from api.ai.priority_algorithm.priority_teamset import PriorityTeamSet, PriorityTeam
from api.models.student import Student
from api.models.team import Team
from tests.test_api.test_ai.test_priority_algorithm.test_mutations.test_local_max import (
    EvenPriority,
)


class TestUtil(unittest.TestCase):
    @classmethod
    def setUp(cls):
        students = [
            Student(_id=1, name="Joe"),
            Student(_id=2, name="John"),
            Student(_id=3, name=""),
            Student(_id=4, name="123"),
        ]
        student_dict = {}
        for student in students:
            student_dict[student.id] = student
        cls.priorities: List[Priority] = [EvenPriority()]
        teams = [
            Team(_id=1, name="Team 1", students=students[0:2]),
            Team(_id=2, name="Team 2", students=students[2:4]),
        ]
        cls.priority_team_set = PriorityTeamSet(
            [
                PriorityTeam(team, [student.id for student in team.students])
                for team in teams
            ]
        )
        cls.students = students
        cls.student_dict = student_dict

    def test_score__returns_correct_score(self):
        # Neither Team satisfies priority
        for team in self.priority_team_set.priority_teams:
            self.assertEqual(0, score(team, self.priorities, self.student_dict))
        # Make both teams satisfy priority
        for student in self.students:
            student._id *= 2
        for team in self.priority_team_set.priority_teams:
            self.assertEqual(24, score(team, self.priorities, self.student_dict))
