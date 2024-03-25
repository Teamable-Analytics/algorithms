import copy
import unittest
from typing import List

from api.ai.priority_algorithm.priority.priority import (
    RequirementPriority,
    DiversityPriority,
    TokenizationPriority,
    ProjectPreferencePriority,
    SocialPreferencePriority,
)
from api.dataclasses.enums import (
    RequirementOperator,
    RequirementsCriteria,
    DiversifyType,
    TokenizationConstraintDirection,
    Relationship,
)
from api.dataclasses.project import ProjectRequirement
from api.dataclasses.student import Student
from api.dataclasses.team import TeamShell
from benchmarking.evaluations.enums import PreferenceDirection
from tests.test_api.test_ai.test_priority_algorithm.test_priority._data import (
    create_social_students,
)


class TestTokenizationPriority(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trivial_team_shell = TeamShell(_id=1)
        cls.tokenized_attribute = 1
        cls.tokenized_attribute_value = 100
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
        cls.student_d = Student(
            _id=2,
            attributes={
                cls.tokenized_attribute: [4],
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
            threshold=3,
            direction=TokenizationConstraintDirection.MIN_OF,
            value=self.tokenized_attribute_value,
        )

        highest_satisfaction = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.student_a,
                self.tokenized_student,
                self.tokenized_student,
                self.tokenized_student,
            ],
            self.trivial_team_shell,
        )
        high_satisfaction = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.tokenized_student,
                self.tokenized_student,
                self.tokenized_student,
                self.tokenized_student,
            ],
            self.trivial_team_shell,
        )
        medium_satisfaction = tokenization_priority.satisfaction(
            [
                self.tokenized_student,
                self.tokenized_student,
                self.tokenized_student,
                self.tokenized_student,
                self.tokenized_student,
            ],
            self.trivial_team_shell,
        )
        medium_satisfaction_2 = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.student_a,
                self.student_a,
                self.student_a,
                self.student_a,
            ],
            self.trivial_team_shell,
        )
        # all we care about is tokenized_student vs non, differences between non_tokenized_students do not matter
        medium_satisfaction_3 = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.student_b,
                self.student_c,
                self.student_d,
                self.student_a,
            ],
            self.trivial_team_shell,
        )
        low_satisfaction = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.student_a,
                self.student_a,
                self.tokenized_student,
                self.tokenized_student,
            ],
            self.trivial_team_shell,
        )
        low_satisfaction_2 = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.student_a,
                self.student_a,
                self.student_a,
                self.tokenized_student,
            ],
            self.trivial_team_shell,
        )

        self.assertEqual(highest_satisfaction, 1)
        self.assertGreater(highest_satisfaction, high_satisfaction)
        self.assertGreater(high_satisfaction, medium_satisfaction)
        self.assertEqual(medium_satisfaction, medium_satisfaction_2)
        self.assertEqual(medium_satisfaction_2, medium_satisfaction_3)
        self.assertGreater(medium_satisfaction, low_satisfaction)
        self.assertEqual(low_satisfaction, low_satisfaction_2)
        self.assertEqual(low_satisfaction, 0)

    def test_satisfaction__concentrate_with_max_of_tokenization(self):
        tokenization_priority = TokenizationPriority(
            attribute_id=self.tokenized_attribute,
            strategy=DiversifyType.CONCENTRATE,
            threshold=3,
            direction=TokenizationConstraintDirection.MAX_OF,
            value=self.tokenized_attribute_value,
        )

        highest_satisfaction = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.student_a,
                self.tokenized_student,
                self.tokenized_student,
                self.tokenized_student,
            ],
            self.trivial_team_shell,
        )
        high_satisfaction = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.student_a,
                self.student_a,
                self.tokenized_student,
                self.tokenized_student,
            ],
            self.trivial_team_shell,
        )
        medium_satisfaction = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.student_a,
                self.student_a,
                self.student_a,
                self.tokenized_student,
            ],
            self.trivial_team_shell,
        )
        medium_satisfaction_2 = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.student_a,
                self.student_a,
                self.student_a,
                self.student_a,
            ],
            self.trivial_team_shell,
        )
        # all we care about is tokenized_student vs non, differences between non_tokenized_students do not matter
        medium_satisfaction_3 = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.student_b,
                self.student_c,
                self.student_d,
                self.student_a,
            ],
            self.trivial_team_shell,
        )
        low_satisfaction = tokenization_priority.satisfaction(
            [
                self.student_a,
                self.tokenized_student,
                self.tokenized_student,
                self.tokenized_student,
                self.tokenized_student,
            ],
            self.trivial_team_shell,
        )
        low_satisfaction_2 = tokenization_priority.satisfaction(
            [
                self.tokenized_student,
                self.tokenized_student,
                self.tokenized_student,
                self.tokenized_student,
                self.tokenized_student,
            ],
            self.trivial_team_shell,
        )

        self.assertEqual(highest_satisfaction, 1)
        self.assertGreater(highest_satisfaction, high_satisfaction)
        self.assertGreater(high_satisfaction, medium_satisfaction)
        self.assertEqual(medium_satisfaction, medium_satisfaction_2)
        self.assertEqual(medium_satisfaction_2, medium_satisfaction_3)
        self.assertGreater(medium_satisfaction, low_satisfaction)
        self.assertEqual(low_satisfaction, low_satisfaction_2)
        self.assertEqual(low_satisfaction, 0)


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
        cls.multi_attribute_id = 2
        cls.trivial_team_shell = TeamShell(_id=1)
        cls.student_a = Student(
            _id=1,
            attributes={
                cls.attribute_id: [1],
                cls.multi_attribute_id: [1, 2, 3],
            },
        )
        cls.student_b = Student(
            _id=2,
            attributes={
                cls.attribute_id: [2],
                cls.multi_attribute_id: [1, 2],
            },
        )
        cls.student_c = Student(
            _id=3,
            attributes={
                cls.attribute_id: [3],
                cls.multi_attribute_id: [1],
            },
        )
        cls.student_d = Student(
            _id=3,
            attributes={
                # intentionally duplicated value
                cls.attribute_id: [3],
                cls.multi_attribute_id: [2],
            },
        )
        cls.student_e = Student(
            _id=3,
            attributes={
                cls.multi_attribute_id: [3],
            },
        )
        cls.student_f = Student(
            _id=3,
            attributes={
                cls.multi_attribute_id: [],
            },
        )

    def test_satisfaction__with_concentrate(self):
        diversity_priority = DiversityPriority(
            attribute_id=self.attribute_id,
            strategy=DiversifyType.CONCENTRATE,
            max_num_choices=1,
        )
        high_satisfaction = diversity_priority.satisfaction(
            ensure_different_ids([self.student_c, self.student_d]),
            self.trivial_team_shell,
        )
        medium_satisfaction = diversity_priority.satisfaction(
            ensure_different_ids([self.student_b, self.student_c, self.student_d]),
            self.trivial_team_shell,
        )
        low_satisfaction = diversity_priority.satisfaction(
            ensure_different_ids([self.student_a, self.student_b, self.student_c]),
            self.trivial_team_shell,
        )

        self.assertGreater(high_satisfaction, medium_satisfaction)
        self.assertGreater(medium_satisfaction, low_satisfaction)

    def test_satisfaction__with_concentrate_and_multi_answers(self):
        diversity_priority = DiversityPriority(
            attribute_id=self.multi_attribute_id,
            strategy=DiversifyType.CONCENTRATE,
            max_num_choices=3,
        )
        highest_satisfaction = diversity_priority.satisfaction(
            ensure_different_ids([self.student_a, self.student_a, self.student_a]),
            self.trivial_team_shell,
        )
        high_satisfaction = diversity_priority.satisfaction(
            ensure_different_ids([self.student_a, self.student_a, self.student_b]),
            self.trivial_team_shell,
        )
        satisfaction_1 = diversity_priority.satisfaction(
            ensure_different_ids([self.student_b, self.student_b, self.student_b]),
            self.trivial_team_shell,
        )
        satisfaction_2 = diversity_priority.satisfaction(
            ensure_different_ids([self.student_b, self.student_b, self.student_c]),
            self.trivial_team_shell,
        )
        satisfaction_3 = diversity_priority.satisfaction(
            ensure_different_ids([self.student_a, self.student_a, self.student_f]),
            self.trivial_team_shell,
        )
        satisfaction_4 = diversity_priority.satisfaction(
            ensure_different_ids([self.student_c, self.student_c, self.student_c]),
            self.trivial_team_shell,
        )
        lowest_satisfaction_1 = diversity_priority.satisfaction(
            ensure_different_ids([self.student_c, self.student_d, self.student_e]),
            self.trivial_team_shell,
        )
        lowest_satisfaction_2 = diversity_priority.satisfaction(
            ensure_different_ids([self.student_f, self.student_f, self.student_f]),
            self.trivial_team_shell,
        )

        self.assertGreater(highest_satisfaction, high_satisfaction)
        self.assertGreater(high_satisfaction, satisfaction_1)
        self.assertGreater(satisfaction_1, satisfaction_2)
        self.assertGreater(satisfaction_2, satisfaction_3)
        self.assertGreaterEqual(satisfaction_3, satisfaction_4)
        self.assertGreater(satisfaction_4, lowest_satisfaction_1)
        self.assertEqual(lowest_satisfaction_1, lowest_satisfaction_2)

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


def ensure_different_ids(students: List[Student]) -> List[Student]:
    # some calculations care about student ids and them being different,
    # but it's easier to write tests without making new students, so ths
    # just lets us fake it whenever
    new_students = []
    for index, student in enumerate(students):
        new_student = copy.deepcopy(student)
        new_student._id = index
        new_students.append(new_student)
    return new_students
