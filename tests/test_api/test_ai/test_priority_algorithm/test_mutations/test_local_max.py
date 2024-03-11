import unittest
from dataclasses import dataclass
from typing import List

from schema import Schema

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet, PriorityTeam
from api.ai.priority_algorithm.mutations import (
    mutate_local_max_random,
    mutate_local_max,
    mutate_local_max_double_random,
)
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.dataclasses.student import Student
from api.dataclasses.team import Team, TeamShell


@dataclass
class EvenPriority(Priority):
    """
    A mock priority to check that all students in a team have an even student id
    """

    def satisfaction(self, students: List[Student], team_shell: TeamShell) -> float:
        for student in students:
            if student.id % 2 == 1:
                return 0
        return 1

    def validate(self) -> bool:
        return True

    @staticmethod
    def get_schema() -> Schema:
        return Schema({})


@dataclass
class JohnPriority(Priority):
    """
    A mock priority that checks if a team has a student named John
    """

    def satisfaction(self, students: List[Student], team_shell: TeamShell) -> float:
        for student in students:
            if student.name == "John":
                return 1
        return 0

    def validate(self) -> bool:
        return True

    @staticmethod
    def get_schema() -> Schema:
        return Schema({})


class TestMutations(unittest.TestCase):
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
