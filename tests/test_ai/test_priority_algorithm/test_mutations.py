import unittest

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

# TODO: Add Priority Interface (fulfilled if student id is even )

class TestMutations(unittest.TestCase):
    students = None

    @classmethod
    def setUpClass(cls):
        cls.students = MockStudentProvider(
            MockStudentProviderSettings(
                number_of_students=20,
                attribute_ranges={
                    ScenarioAttribute.GENDER.value: [
                        (Gender.MALE, 1 - 0.2),
                        (Gender.FEMALE, 0.2),
                    ]
                },
            )
        ).get()
        print(cls.students)
        cls.student_dict = {}
        for student in cls.students:
            cls.student_dict[student.id] = student
        cls.priorities = [
            TokenizationPriority(
                ScenarioAttribute.GENDER.value,
                DiversifyType.DIVERSIFY,
                TokenizationConstraintDirection.MIN_OF,
                2,
                "1",
            )
        ]
        teams = [
            Team(1, "Team 1", 1, cls.students[0:5]),
            Team(2, "Team 2", 1, cls.students[5:10]),
            Team(3, "Team 3", 1, cls.students[10:15]),
            Team(4, "Team 4", 1, cls.students[15:20]),
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

    def test_local_max__modifies_lowest_teams_only(self):
        # TODO: Complete this
        assert 1 == 1

    def test_score__returns_correct_score(self):
        for team in self.priority_team_set.priority_teams:
            self.assertEqual(24, score(team, self.priorities, self.student_dict))
