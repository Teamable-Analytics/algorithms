import unittest

from api.ai.priority_algorithm.priority.priority import (
    RequirementPriority,
    DiversityPriority,
)
from api.models.enums import RequirementOperator, RequirementsCriteria, DiversifyType
from api.models.project import ProjectRequirement
from api.models.student import Student
from api.models.team import TeamShell


class TestRequirementPriority(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.team_shell_1 = TeamShell(
            _id=1,
            requirements=[
                ProjectRequirement(
                    attribute=1,
                    operator=RequirementOperator.EXACTLY,
                    value=1,
                ),
                ProjectRequirement(
                    attribute=2,
                    operator=RequirementOperator.EXACTLY,
                    value=2,
                ),
            ],
        )
        cls.student_a = Student(
            _id=1,
            attributes={
                1: [1],
            },
        )
        cls.student_b = Student(
            _id=2,
            attributes={
                2: [2],
            },
        )
        cls.student_c = Student(
            _id=3,
            attributes={
                3: [3],
            },
        )

    def test_satisfaction__with_student_attributes_are_relevant_criteria(self):
        requirement_priority = RequirementPriority(
            criteria=RequirementsCriteria.STUDENT_ATTRIBUTES_ARE_RELEVANT
        )
        high_satisfaction = requirement_priority.satisfaction(
            [self.student_a, self.student_b], self.team_shell_1
        )
        medium_satisfaction = requirement_priority.satisfaction(
            [self.student_b, self.student_c], self.team_shell_1
        )
        low_satisfaction = requirement_priority.satisfaction(
            [self.student_c], self.team_shell_1
        )

        self.assertGreater(high_satisfaction, medium_satisfaction)
        self.assertGreater(medium_satisfaction, low_satisfaction)

    def test_satisfaction__with_project_requirements_are_satisfied_criteria(self):
        requirement_priority = RequirementPriority(
            criteria=RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED
        )
        high_satisfaction = requirement_priority.satisfaction(
            [self.student_a, self.student_b], self.team_shell_1
        )
        medium_satisfaction = requirement_priority.satisfaction(
            [self.student_a], self.team_shell_1
        )
        low_satisfaction = requirement_priority.satisfaction(
            [self.student_c], self.team_shell_1
        )

        self.assertGreater(high_satisfaction, medium_satisfaction)
        self.assertGreater(medium_satisfaction, low_satisfaction)


class TestDiversityPriority(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.attribute_id = 1
        cls.trivial_team_shell = TeamShell(_id=1)
        cls.student_a = Student(
            _id=1,
            attributes={
                cls.attribute_id: [1],
            },
        )
        cls.student_b = Student(
            _id=2,
            attributes={
                cls.attribute_id: [2],
            },
        )
        cls.student_c = Student(
            _id=3,
            attributes={
                cls.attribute_id: [3],
            },
        )
        cls.student_d = Student(
            _id=3,
            attributes={
                # intentionally duplicated value
                cls.attribute_id: [3],
            },
        )

    def test_satisfaction__with_concentrate(self):
        diversity_priority = DiversityPriority(
            attribute_id=self.attribute_id, strategy=DiversifyType.CONCENTRATE
        )
        high_satisfaction = diversity_priority.satisfaction(
            [self.student_c, self.student_d], self.trivial_team_shell
        )
        medium_satisfaction = diversity_priority.satisfaction(
            [self.student_b, self.student_c, self.student_d], self.trivial_team_shell
        )
        low_satisfaction = diversity_priority.satisfaction(
            [self.student_a, self.student_b, self.student_c], self.trivial_team_shell
        )

        self.assertGreater(high_satisfaction, medium_satisfaction)
        self.assertGreater(medium_satisfaction, low_satisfaction)

    def test_satisfaction__with_diversify(self):
        diversity_priority = DiversityPriority(
            attribute_id=self.attribute_id, strategy=DiversifyType.DIVERSIFY
        )
        high_satisfaction = diversity_priority.satisfaction(
            [self.student_a, self.student_b, self.student_c], self.trivial_team_shell
        )
        medium_satisfaction = diversity_priority.satisfaction(
            [self.student_a, self.student_b, self.student_c, self.student_d],
            self.trivial_team_shell,
        )
        low_satisfaction = diversity_priority.satisfaction(
            [self.student_c, self.student_d], self.trivial_team_shell
        )

        self.assertGreater(high_satisfaction, medium_satisfaction)
        self.assertGreater(medium_satisfaction, low_satisfaction)
