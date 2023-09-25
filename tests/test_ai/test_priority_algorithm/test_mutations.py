import unittest

from ai.priority_algorithm.priority import TokenizationPriority
from ai.priority_algorithm.priority_teamset import PriorityTeamSet, PriorityTeam
from benchmarking.data.interfaces import MockStudentProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProvider
from models.enums import DiversifyType, TokenizationConstraintDirection
from models.student import Student
from models.team import Team


class TestMutations(unittest.TestCase):
    students = None

    @classmethod
    def setUpClass(cls):
        cls.students = MockStudentProvider(
            MockStudentProviderSettings(number_of_students=20)
        ).get()
        cls.student_dict = {}
        for student in cls.students:
            cls.student_dict[student.id] = student
        cls.priorities = [TokenizationPriority(1, DiversifyType.DIVERSIFY, TokenizationConstraintDirection.MIN_OF, 2, "1")]
        Team(1, "Team 1", )


    def generatePriorityTeams(self) -> PriorityTeamSet:



    def test_local_max__returns_priority_teams(self):
        # TODO: Implement
        assert 1 == 1

    def test_local_max__modifies_lowest_teams_only(self):
        # TODO: Implement
        assert 1 == 1
