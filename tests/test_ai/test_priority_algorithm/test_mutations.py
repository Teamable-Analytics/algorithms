import unittest
from dataclasses import dataclass
from typing import List

from ai.priority_algorithm.interfaces import Priority
from ai.priority_algorithm.mutations import mutate_local_max, score
from ai.priority_algorithm.priority import TokenizationPriority
from ai.priority_algorithm.priority_teamset import PriorityTeamSet, PriorityTeam
from benchmarking.data.interfaces import MockStudentProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProvider
from models.enums import (
    DiversifyType,
    TokenizationConstraintDirection,
    ScenarioAttribute,
    Gender,
)
from models.student import Student
from models.team import Team


@dataclass
class EvenPriority(Priority):
    """
    A mock priority to check that all students in a team have an even student id
    """

    def satisfied_by(self, students: List[Student]) -> bool:
        for student in students:
            if student.id % 2 == 1:
                return False
        return True

    def validate(self) -> bool:
        return True


@dataclass
class JohnPriority(Priority):
    """
    A mock priority that checks if a team has a student named John
    """

    def satisfied_by(self, students: List[Student]) -> bool:
        for student in students:
            if student.name == "John":
                return True
        return False

    def validate(self) -> bool:
        return True


class TestMutations(unittest.TestCase):
    students = None

    @classmethod
    def setUp(cls):
        cls.students = [
            Student(_id=1, name="John"),
            Student(_id=2, name="Joe"),
            Student(_id=3, name=""),
            Student(_id=4, name="123")
        ]
        cls.student_dict = {}
        for student in cls.students:
            cls.student_dict[student.id] = student
        cls.priorities = [
            EvenPriority()
        ]
        teams = [
            Team(1, "Team 1", 1, cls.students[0:2]),
            Team(2, "Team 2", 1, cls.students[2:4]),
        ]
        cls.priority_team_set = PriorityTeamSet(
            [
                PriorityTeam(team, [student.id for student in team.students])
                for team in teams
            ]
        )

    def test_local_max__returns_priority_teams(self):
        priority_team_set = mutate_local_max(
            self.priority_team_set, self.priorities, self.student_dict
        )
        self.assertIsInstance(priority_team_set, PriorityTeamSet)
        for team in priority_team_set.priority_teams:
            self.assertIsInstance(team, PriorityTeam)

    def test_local_max__improves_team_based_on_priority(self):
        priority_team_set = mutate_local_max(
            self.priority_team_set, self.priorities, self.student_dict
        )
        self.assertEqual(12, priority_team_set.calculate_score(self.priorities, self.student_dict))

    def test_score__returns_correct_score(self):
        # Neither Team satisfies priority
        for team in self.priority_team_set.priority_teams:
            self.assertEqual(0, score(team, self.priorities, self.student_dict))
        # Make both teams satisfy priority
        for student in self.students:
            student._id *= 2
        for team in self.priority_team_set.priority_teams:
            self.assertEqual(24, score(team, self.priorities, self.student_dict))

    def test_local_max__improves_team_with_two_priorities(self):
        self.priorities.append(JohnPriority())
        priority_team_set = mutate_local_max(
            self.priority_team_set, self.priorities, self.student_dict
        )
        self.assertEqual(312, priority_team_set.calculate_score(self.priorities, self.student_dict))
