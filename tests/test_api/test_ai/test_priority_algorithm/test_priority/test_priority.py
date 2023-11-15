import unittest

from api.ai.priority_algorithm.priority.priority import (
    RequirementPriority,
    DiversityPriority,
    TokenizationPriority,
    ProjectPreferencePriority,
)
from api.models.enums import (
    RequirementOperator,
    RequirementsCriteria,
    DiversifyType,
    TokenizationConstraintDirection,
)
from api.models.project import ProjectRequirement
from api.models.student import Student
from api.models.team import TeamShell
from benchmarking.evaluations.enums import PreferenceDirection


class TestTokenizationPriority(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trivial_team_shell = TeamShell(_id=1)
        cls.tokenized_attribute = 1
        cls.tokenized_attribute_value = 4
        cls.student_a = Student(
            _id=1,
            attributes={
                cls.tokenized_attribute: [1],
            },
        )
        cls.student_b = Student(
            _id=2,
            attributes={
                cls.tokenized_attribute: [2],
            },
        )
        cls.student_c = Student(
            _id=2,
            attributes={
                cls.tokenized_attribute: [3],
            },
        )
        cls.tokenized_student = Student(
            _id=3,
            attributes={
                cls.tokenized_attribute: [cls.tokenized_attribute_value],
            },
        )

    def test_satisfaction__diversify_with_min_of_tokenization(self):
        tokenization_priority = TokenizationPriority(
            attribute_id=self.tokenized_attribute,
            strategy=DiversifyType.DIVERSIFY,
            threshold=2,
            direction=TokenizationConstraintDirection.MIN_OF,
            value=self.tokenized_attribute_value,
        )

        high_satisfaction = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.student_b,
                self.tokenized_student,
                self.tokenized_student,
            ],
            self.trivial_team_shell,
        )
        medium_satisfaction = tokenization_priority.satisfaction(
            [self.student_a, self.student_b, self.student_c], self.trivial_team_shell
        )
        medium_satisfaction_2 = tokenization_priority.satisfaction(
            [self.tokenized_student, self.tokenized_student, self.tokenized_student],
            self.trivial_team_shell,
        )
        low_satisfaction = tokenization_priority.satisfaction(
            [self.student_a, self.student_a, self.student_a], self.trivial_team_shell
        )
        lowest_satisfaction = tokenization_priority.satisfaction(
            [self.student_a, self.student_b, self.tokenized_student],
            self.trivial_team_shell,
        )

        self.assertGreaterEqual(high_satisfaction, medium_satisfaction)
        self.assertGreater(high_satisfaction, medium_satisfaction_2)
        self.assertGreater(medium_satisfaction, low_satisfaction)
        self.assertGreater(medium_satisfaction_2, lowest_satisfaction)
        self.assertGreater(low_satisfaction, lowest_satisfaction)

    def test_satisfaction__concentrate_with_max_of_tokenization(self):
        tokenization_priority = TokenizationPriority(
            attribute_id=self.tokenized_attribute,
            strategy=DiversifyType.CONCENTRATE,
            threshold=2,
            direction=TokenizationConstraintDirection.MAX_OF,
            value=self.tokenized_attribute_value,
        )

        high_satisfaction = tokenization_priority.satisfaction(
            [self.student_a, self.student_a, self.student_a], self.trivial_team_shell
        )
        medium_satisfaction = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.student_a,
                self.tokenized_student,
                self.tokenized_student,
            ],
            self.trivial_team_shell,
        )
        low_satisfaction = tokenization_priority.satisfaction(
            [self.student_a, self.student_b, self.student_c], self.trivial_team_shell
        )
        lowest_satisfaction = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.tokenized_student,
                self.tokenized_student,
                self.tokenized_student,
            ],
            self.trivial_team_shell,
        )

        self.assertGreaterEqual(high_satisfaction, medium_satisfaction)
        self.assertGreater(medium_satisfaction, low_satisfaction)
        self.assertGreater(low_satisfaction, lowest_satisfaction)


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


class TestProjectPreferencePriority(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_id = 100
        cls.team_shell = TeamShell(_id=1, project_id=cls.project_id)
        cls.max_project_preferences = 3
        cls.student_with_correct_preference = Student(
            _id=1,
            project_preferences=[cls.project_id, 2, 3],
        )
        cls.student_b = Student(_id=2, project_preferences=[1, cls.project_id, 3])
        cls.student_c = Student(_id=3, project_preferences=[1, 2, cls.project_id])
        cls.student_irrelevant_pref = Student(_id=3, project_preferences=[1, 2, 3])
        cls.student_no_pref = Student(_id=3, project_preferences=[])

    def test_satisfaction__doesnt_care_about_team_size(self):
        project_preference_priority = ProjectPreferencePriority(
            max_project_preferences=self.max_project_preferences,
            direction=PreferenceDirection.INCLUDE,
        )
        satisfaction = project_preference_priority.satisfaction(
            [self.student_with_correct_preference], self.team_shell
        )
        also_satisfaction = project_preference_priority.satisfaction(
            [
                self.student_with_correct_preference,
                self.student_with_correct_preference,
                self.student_with_correct_preference,
            ],
            self.team_shell,
        )
        self.assertEqual(satisfaction, also_satisfaction)

        satisfaction_2 = project_preference_priority.satisfaction(
            [self.student_with_correct_preference], self.team_shell
        )
        also_satisfaction_2 = project_preference_priority.satisfaction(
            [
                self.student_with_correct_preference,
                self.student_with_correct_preference,
                self.student_with_correct_preference,
            ],
            self.team_shell,
        )
        self.assertEqual(satisfaction_2, also_satisfaction_2)

        project_preference_priority_excludes = ProjectPreferencePriority(
            max_project_preferences=self.max_project_preferences,
            direction=PreferenceDirection.EXCLUDE,
        )
        satisfaction_3 = project_preference_priority_excludes.satisfaction(
            [self.student_with_correct_preference], self.team_shell
        )
        also_satisfaction_3 = project_preference_priority_excludes.satisfaction(
            [
                self.student_with_correct_preference,
                self.student_with_correct_preference,
                self.student_with_correct_preference,
            ],
            self.team_shell,
        )
        self.assertEqual(satisfaction_3, also_satisfaction_3)

    def test_satisfaction__with_including_preferences(self):
        project_preference_priority = ProjectPreferencePriority(
            max_project_preferences=self.max_project_preferences,
            direction=PreferenceDirection.INCLUDE,
        )
        high_satisfaction = project_preference_priority.satisfaction(
            [self.student_with_correct_preference], self.team_shell
        )
        medium_satisfaction = project_preference_priority.satisfaction(
            [self.student_b], self.team_shell
        )
        low_satisfaction = project_preference_priority.satisfaction(
            [self.student_c], self.team_shell
        )
        lowest_satisfaction = project_preference_priority.satisfaction(
            [self.student_no_pref], self.team_shell
        )
        also_lowest_satisfaction = project_preference_priority.satisfaction(
            [self.student_irrelevant_pref], self.team_shell
        )

        self.assertGreater(high_satisfaction, medium_satisfaction)
        self.assertGreater(medium_satisfaction, low_satisfaction)
        self.assertGreater(low_satisfaction, lowest_satisfaction)
        self.assertGreater(low_satisfaction, also_lowest_satisfaction)
        self.assertEqual(lowest_satisfaction, also_lowest_satisfaction)

    def test_satisfaction__with_excluding_preferences(self):
        project_preference_priority = ProjectPreferencePriority(
            max_project_preferences=self.max_project_preferences,
            direction=PreferenceDirection.EXCLUDE,
        )
        high_satisfaction = project_preference_priority.satisfaction(
            [self.student_no_pref], self.team_shell
        )
        also_high_satisfaction = project_preference_priority.satisfaction(
            [self.student_irrelevant_pref], self.team_shell
        )
        medium_satisfaction = project_preference_priority.satisfaction(
            [self.student_c], self.team_shell
        )
        low_satisfaction = project_preference_priority.satisfaction(
            [self.student_b], self.team_shell
        )
        lowest_satisfaction = project_preference_priority.satisfaction(
            [self.student_with_correct_preference], self.team_shell
        )

        self.assertEqual(high_satisfaction, also_high_satisfaction)
        self.assertGreater(high_satisfaction, medium_satisfaction)
        self.assertGreater(also_high_satisfaction, medium_satisfaction)
        self.assertGreater(medium_satisfaction, low_satisfaction)
        self.assertGreater(low_satisfaction, lowest_satisfaction)
