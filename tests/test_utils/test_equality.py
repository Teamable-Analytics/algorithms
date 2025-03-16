import copy
import unittest

from algorithms.dataclasses.enums import RequirementOperator
from algorithms.dataclasses.project import ProjectRequirement
from algorithms.dataclasses.student import Student
from algorithms.dataclasses.team import Team
from utils.equality import (
    are_students_equal_ignoring_team,
    are_teams_equal_ignoring_students,
    teams_are_equal,
)


class TestEqualityHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.student_1_a = Student(_id=1)
        cls.student_2_a = Student(_id=2)
        cls.team_a = Team(
            _id=1,
            students=[
                cls.student_1_a,
                cls.student_2_a,
            ],
        )
        cls.student_1_b = Student(_id=1)
        cls.student_2_b = Student(_id=2)
        cls.team_b = Team(
            _id=1,
            students=[
                cls.student_1_b,
                cls.student_2_b,
            ],
        )
        cls.team_c = Team(
            _id=1,
            students=[
                cls.student_1_b,
            ],
        )
        cls.team_d = Team(
            _id=2,
            students=[
                cls.student_1_a,
                cls.student_1_b,
            ],
        )

    def test_are_students_equal_ignoring_team(self):
        self.assertTrue(
            are_students_equal_ignoring_team(self.student_1_a, self.student_1_b)
        )
        self.assertFalse(
            are_students_equal_ignoring_team(self.student_1_a, self.student_2_b)
        )

    def test_are_teams_equal_ignoring_students(self):
        self.assertTrue(are_teams_equal_ignoring_students(self.team_a, self.team_b))
        self.assertTrue(are_teams_equal_ignoring_students(self.team_a, self.team_c))
        self.assertFalse(are_teams_equal_ignoring_students(self.team_c, self.team_d))

    def test_teams_are_equal(self):
        self.assertFalse(teams_are_equal(self.team_a, self.team_b))
        self.assertFalse(teams_are_equal(self.team_a, self.team_c))
        self.assertFalse(teams_are_equal(self.team_a, self.team_d))

        team = Team(
            _id=7,
            name="Test Team",
            project_id=100,
            requirements=[
                ProjectRequirement(
                    attribute=1,
                    operator=RequirementOperator.EXACTLY,
                    value=1,
                ),
                ProjectRequirement(
                    attribute=2,
                    operator=RequirementOperator.EXACTLY,
                    value=1,
                ),
            ],
        )
        team_clone = copy.deepcopy(team)
        self.assertTrue(teams_are_equal(team, team_clone))

        team_with_switched_requirements = Team(
            _id=7,
            name="Test Team",
            project_id=100,
            requirements=[
                ProjectRequirement(
                    attribute=2,
                    operator=RequirementOperator.EXACTLY,
                    value=1,
                ),
                ProjectRequirement(
                    attribute=1,
                    operator=RequirementOperator.EXACTLY,
                    value=1,
                ),
            ],
        )
        self.assertTrue(team, team_with_switched_requirements)
