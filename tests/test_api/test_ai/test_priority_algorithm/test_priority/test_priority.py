import unittest

from api.ai.priority_algorithm.priority.priority import (
    RequirementPriority,
    DiversityPriority,
    TokenizationPriority,
    ProjectPreferencePriority,
    SocialPreferencePriority,
)
from api.models.enums import (
    RequirementOperator,
    RequirementsCriteria,
    DiversifyType,
    TokenizationConstraintDirection,
    Relationship,
)
from api.models.project import ProjectRequirement
from api.models.student import Student
from api.models.team import TeamShell
from benchmarking.evaluations.enums import PreferenceDirection
from tests.test_api.test_ai.test_priority_algorithm.test_priority._data import (
    create_social_students,
)


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


class TestSocialPriority(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trivial_team_shell = TeamShell(_id=1)

    def test_satisfaction(self):
        social_priority = SocialPreferencePriority(
            max_num_friends=2,
            max_num_enemies=2,
        )

        all_friends = social_priority.satisfaction(
            create_social_students(num_friends=3),
            self.trivial_team_shell,
        )
        friend_2_neutral_1 = social_priority.satisfaction(
            create_social_students(num_friends=2, num_neutrals=1),
            self.trivial_team_shell,
        )
        friend_2_hater_1 = social_priority.satisfaction(
            create_social_students(num_friends=2, num_haters=1),
            self.trivial_team_shell,
        )
        friend_2_outcast_1 = social_priority.satisfaction(
            create_social_students(num_friends=2, num_outcasts=1),
            self.trivial_team_shell,
        )
        neutral_2_hater_1 = social_priority.satisfaction(
            create_social_students(num_neutrals=2, num_haters=1),
            self.trivial_team_shell,
        )
        neutral_2_outcast_1 = social_priority.satisfaction(
            create_social_students(num_neutrals=2, num_outcasts=1),
            self.trivial_team_shell,
        )
        enemy_2_neutral_1 = social_priority.satisfaction(
            create_social_students(num_enemies=2, num_neutrals=1),
            self.trivial_team_shell,
        )
        all_enemies = social_priority.satisfaction(
            create_social_students(num_enemies=3),
            self.trivial_team_shell,
        )
        all_neutrals = social_priority.satisfaction(
            create_social_students(num_neutrals=3),
            self.trivial_team_shell,
        )
        friend_2_fan_1 = social_priority.satisfaction(
            create_social_students(num_friends=2, num_fans=1),
            self.trivial_team_shell,
        )
        neutral_2_fan_1 = social_priority.satisfaction(
            create_social_students(num_neutrals=2, num_fans=1),
            self.trivial_team_shell,
        )
        enemy_2_fan_1 = social_priority.satisfaction(
            create_social_students(num_enemies=2, num_fans=1),
            self.trivial_team_shell,
        )
        friend_cycle = social_priority.satisfaction(
            [
                Student(_id=1, relationships={2: Relationship.FRIEND}),
                Student(_id=2, relationships={3: Relationship.FRIEND}),
                Student(_id=3, relationships={1: Relationship.FRIEND}),
            ],
            self.trivial_team_shell,
        )
        enemy_cycle = social_priority.satisfaction(
            [
                Student(_id=1, relationships={2: Relationship.ENEMY}),
                Student(_id=2, relationships={3: Relationship.ENEMY}),
                Student(_id=3, relationships={1: Relationship.ENEMY}),
            ],
            self.trivial_team_shell,
        )

        self.assertGreater(all_friends, friend_2_fan_1)
        self.assertGreater(friend_2_fan_1, friend_cycle)
        self.assertGreater(friend_cycle, neutral_2_fan_1)
        self.assertEqual(neutral_2_fan_1, friend_2_neutral_1)
        self.assertGreater(friend_2_neutral_1, all_neutrals)
        self.assertGreater(all_neutrals, friend_2_hater_1)
        self.assertEqual(friend_2_hater_1, enemy_2_fan_1)
        self.assertGreater(enemy_2_fan_1, neutral_2_hater_1)
        self.assertEqual(neutral_2_hater_1, enemy_2_neutral_1)
        self.assertGreater(enemy_2_neutral_1, friend_2_outcast_1)
        self.assertGreater(friend_2_outcast_1, enemy_cycle)
        self.assertGreater(enemy_cycle, neutral_2_outcast_1)
        self.assertGreater(neutral_2_outcast_1, all_enemies)
