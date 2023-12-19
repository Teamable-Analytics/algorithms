import unittest
from typing import Literal, List

import numpy as np

from api.models.enums import Gpa, Relationship
from api.models.student import Student
from benchmarking.data.simulated_data.mock_student_provider import (
    attribute_values_from_range,
    create_mock_students,
    MockStudentProvider,
    random_choice,
    MockStudentProviderSettings,
    num_values_for_attribute,
)
from utils.validation import is_unique


class TestMockStudentProvider(unittest.TestCase):
    def test_get__returns_student_objects(self):
        students = MockStudentProvider(
            MockStudentProviderSettings(number_of_students=10)
        ).get()

        for student in students:
            self.assertIsInstance(student, Student)

    def test_max_project_preferences__are_correctly_inferred(self):
        max_project_preferences_1 = MockStudentProvider(
            MockStudentProviderSettings(
                number_of_students=10,
                project_preference_options=[1, 2, 3],
                num_project_preferences_per_student=3,
            )
        ).max_project_preferences_per_student

        self.assertEqual(max_project_preferences_1, 3)


class TestMockStudentProviderHelpers(unittest.TestCase):
    def test_create_mock_students__student_has_correct_num_values_for_attribute(self):
        students = create_mock_students(
            number_of_students=1,
            number_of_friends=0,
            number_of_enemies=0,
            friend_distribution="random",
            attribute_ranges={
                1: [1, 2, 3, 4],
                2: [1, 2, 3, 4],
                3: [1, 2, 3, 4],
            },
            num_values_per_attribute={
                1: 3,
                2: 2,
                3: 1,
            },
            project_preference_options=[],
            num_project_preferences_per_student=0,
        )

        student = students[0]
        self.assertEqual(len(student.attributes[1]), 3)
        self.assertEqual(len(student.attributes[2]), 2)
        self.assertEqual(len(student.attributes[3]), 1)

    def test_create_mock_students__students_have_correct_project_preferences(self):
        students = create_mock_students(
            number_of_students=1,
            number_of_friends=0,
            number_of_enemies=0,
            friend_distribution="random",
            attribute_ranges={},
            num_values_per_attribute={},
            project_preference_options=[1, 2, 3],
            num_project_preferences_per_student=3,
        )

        student = students[0]
        self.assertEqual(len(student.project_preferences), 3)
        self.assertTrue(is_unique(student.project_preferences))

    def test_create_mock_students__student_has_num_values_for_attribute_within_range(
        self,
    ):
        students = create_mock_students(
            number_of_students=5,
            number_of_friends=0,
            number_of_enemies=0,
            friend_distribution="random",
            attribute_ranges={
                1: [1, 2, 3, 4],
                2: [1, 2, 3, 4],
                3: [1, 2, 3, 4],
            },
            num_values_per_attribute={
                1: (2, 4),
                2: (1, 3),
                3: (3, 4),
            },
            project_preference_options=[],
            num_project_preferences_per_student=0,
        )

        for student in students:
            self.assertTrue(2 <= len(student.attributes[1]) < 4)
            self.assertTrue(1 <= len(student.attributes[2]) < 3)
            self.assertTrue(3 <= len(student.attributes[3]) < 4)

    def test_create_mock_students__students_have_correct_friend_and_enemy_count(self):
        for i in [1, 5, 10]:
            students = create_mock_students(
                number_of_students=i * 2 + 1,
                number_of_friends=i,
                number_of_enemies=i,
                friend_distribution="random",
                attribute_ranges={},
                num_values_per_attribute={},
                project_preference_options=[],
                num_project_preferences_per_student=0,
            )
            for student in students:
                self.assertGreaterEqual(
                    i,
                    len(
                        [
                            r
                            for r in student.relationships.values()
                            if r == Relationship.FRIEND
                        ]
                    ),
                )
                self.assertGreaterEqual(
                    i,
                    len(
                        [
                            r
                            for r in student.relationships.values()
                            if r == Relationship.ENEMY
                        ]
                    ),
                )

    def test_create_mock_students__each_student_has_correct_num_friends_and_enemies(
        self,
    ):
        dist_types: List[Literal["random", "cluster"]] = ["random", "cluster"]
        for dist_type in dist_types:
            students = create_mock_students(
                number_of_students=10,
                number_of_friends=4,
                number_of_enemies=2,
                friend_distribution=dist_type,
                attribute_ranges={},
                num_values_per_attribute={},
                project_preference_options=[],
                num_project_preferences_per_student=0,
            )

            for student in students:
                num_friends = len(
                    [
                        1
                        for stu_id, relation in student.relationships.items()
                        if relation == Relationship.FRIEND
                    ]
                )
                num_enemies = len(
                    [
                        1
                        for stu_id, relation in student.relationships.items()
                        if relation == Relationship.ENEMY
                    ]
                )

                self.assertEqual(4, num_friends)
                self.assertEqual(2, num_enemies)

    def test_create_mock_students__each_student_has_correct_num_friends_and_enemies_non_divisible_class_size(
        self,
    ):
        dist_types: List[Literal["random", "cluster"]] = ["random", "cluster"]
        for dist_type in dist_types:
            students = create_mock_students(
                number_of_students=10,
                number_of_friends=3,
                number_of_enemies=2,
                friend_distribution=dist_type,
                attribute_ranges={},
                num_values_per_attribute={},
                project_preference_options=[],
                num_project_preferences_per_student=0,
            )

            for student in students:
                num_friends = len(
                    [
                        1
                        for stu_id, relation in student.relationships.items()
                        if relation == Relationship.FRIEND
                    ]
                )
                num_enemies = len(
                    [
                        1
                        for stu_id, relation in student.relationships.items()
                        if relation == Relationship.ENEMY
                    ]
                )

                self.assertEqual(3, num_friends)
                self.assertEqual(2, num_enemies)

    def test_create_mock_students__class_size_too_small(self):
        self.assertRaises(
            ValueError,
            lambda: create_mock_students(
                number_of_students=2,
                number_of_friends=4,
                number_of_enemies=1,
                friend_distribution="random",
                attribute_ranges={},
                num_values_per_attribute={},
                project_preference_options=[],
                num_project_preferences_per_student=0,
            ),
        )

    def test_create_mock_students__friend_cannot_be_enemy(self):
        dist_types: List[Literal["random", "cluster"]] = ["random", "cluster"]
        for dist_type in dist_types:
            students = create_mock_students(
                number_of_students=10,
                number_of_friends=3,
                number_of_enemies=2,
                friend_distribution=dist_type,
                attribute_ranges={},
                num_values_per_attribute={},
                project_preference_options=[],
                num_project_preferences_per_student=0,
            )

            for student in students:
                friends = [
                    friend_id
                    for friend_id, relation in student.relationships.items()
                    if relation == Relationship.FRIEND
                ]
                enemies = [
                    enemy_id
                    for enemy_id, relation in student.relationships.items()
                    if relation == Relationship.ENEMY
                ]

                for friend in friends:
                    self.assertNotIn(friend, enemies)

    def test_create_mock_students__cluster_setting_returns_clustered_students(self):
        students = create_mock_students(
            number_of_students=12,
            number_of_friends=3,
            number_of_enemies=2,
            friend_distribution="cluster",
            attribute_ranges={},
            num_values_per_attribute={},
            project_preference_options=[],
            num_project_preferences_per_student=0,
        )

        cliques: List[List[int]] = []
        for student in students:
            friends = [
                friend_id
                for friend_id, relation in student.relationships.items()
                if relation == Relationship.FRIEND
            ]

            # Check if current student is assigned to a clique yet
            my_clique = None
            for clique in cliques:
                if student.id in clique:
                    my_clique = clique
                    break

            if my_clique:
                # Check that clique contains all friends
                self.assertTrue(all([friend in my_clique for friend in friends]))
            else:
                # If not in clique yet, create one
                cliques.append([student.id, *friends])

        self.assertEqual(3, len(cliques))

    def test_create_mock_students__students_are_reproducible(self):
        dist_types: List[Literal["random", "cluster"]] = ["random", "cluster"]
        for dist_type in dist_types:
            students_1 = create_mock_students(
                number_of_students=4,
                number_of_friends=2,
                number_of_enemies=1,
                friend_distribution=dist_type,
                attribute_ranges={},
                num_values_per_attribute={},
                project_preference_options=[],
                num_project_preferences_per_student=0,
                random_seed=1,
            )

            students_2 = create_mock_students(
                number_of_students=4,
                number_of_friends=2,
                number_of_enemies=1,
                friend_distribution=dist_type,
                attribute_ranges={},
                num_values_per_attribute={},
                project_preference_options=[],
                num_project_preferences_per_student=0,
                random_seed=1,
            )

            self.assertListEqual(students_1, students_2)

    def test_num_values_for_attribute__returns_int_within_range(self):
        test_range = (5, 12)
        for _ in range(50):
            value = num_values_for_attribute(test_range)
            self.assertIsInstance(value, int)
            self.assertGreaterEqual(value, 5)
            self.assertLessEqual(value, 12)

    def test_random_choice__always_returns_list_of_int(self):
        values_1 = random_choice(possible_values=[1, 2, 3], size=1)
        values_2 = random_choice(possible_values=[1, 2, 3], size=2)
        values_3 = random_choice(possible_values=list(range(0, 100)), size=100)

        for value in [values_1, values_2, values_3]:
            self.assertIsInstance(value, list)
            self.assertIsInstance(value[0], int)
            self.assertIsInstance(value[-1], int)

    def test_attribute_values_from_range__multiple_values_for_attribute_are_selected_without_replacement(
        self,
    ):
        for _ in range(100):
            # FIXME: This test is (technically) a little flaky 😬
            # run this multiple times so that this test cannot accidentally
            #   pass even if the values are selected with replacement
            values_1 = attribute_values_from_range([10, 20, 30], num_values=3, allow_probabilistic_generation=True)
            self.assertListEqual([10, 20, 30], sorted(values_1))

            values_2 = attribute_values_from_range(
                [(10, 0.2), (20, 0.3), (30, 0.5)], num_values=3
            )
            self.assertListEqual([10, 20, 30], sorted(values_2))

            values_3 = attribute_values_from_range([Gpa.A, Gpa.B, Gpa.C], num_values=3, allow_probabilistic_generation=True)
            self.assertListEqual(
                sorted([Gpa.A.value, Gpa.B.value, Gpa.C.value]), sorted(values_3)
            )

            values_4 = attribute_values_from_range(
                [(Gpa.A, 0.2), (Gpa.B, 0.3), (Gpa.C, 0.5)], num_values=3, allow_probabilistic_generation=True
            )
            self.assertListEqual(
                sorted([Gpa.A.value, Gpa.B.value, Gpa.C.value]), sorted(values_4)
            )

    def test_attribute_values_from_range__always_returns_correctly_sized_list(self):
        num_values_list = [1, 2, 3]
        for num_values in num_values_list:
            """
            Test for each of the union types of AttributeRangeConfig
            AttributeRangeConfig = Union[
                List[int],
                List[Tuple[int, float]],
                List[AttributeValueEnum],
                List[Tuple[AttributeValueEnum, float]],
            ]
            """
            self.assertEqual(
                len(attribute_values_from_range([10, 20, 30], num_values=num_values, allow_probabilistic_generation=True)),
                num_values,
            )
            self.assertEqual(
                len(
                    attribute_values_from_range(
                        [(10, 0.2), (20, 0.3), (30, 0.5)], num_values=num_values, allow_probabilistic_generation=True
                    )
                ),
                num_values,
            )
            self.assertEqual(
                len(
                    attribute_values_from_range(
                        [Gpa.A, Gpa.B, Gpa.C], num_values=num_values, allow_probabilistic_generation=True
                    )
                ),
                num_values,
            )
            self.assertEqual(
                len(
                    attribute_values_from_range(
                        [(Gpa.A, 0.2), (Gpa.B, 0.3), (Gpa.C, 0.5)],
                        num_values=num_values,
                        allow_probabilistic_generation=True,
                    )
                ),
                num_values,
            )

    def test_attribute_values_from_range__errors_with_empty_range_config(self):
        with self.assertRaises(Exception):
            attribute_values_from_range([])

    def test_all__reproducible_with_seed(self):
        num_values_for_attribute_values = []
        test_range_1 = (1, 1000)
        for _ in range(50):
            rng = np.random.default_rng(1)
            num_values_for_attribute_values.append(
                num_values_for_attribute(test_range_1, generator=rng)
            )
        self.assertEqual(len(set(num_values_for_attribute_values)), 1)

        random_choice_values = []
        for _ in range(50):
            rng = np.random.default_rng(1)
            random_choice_values.extend(
                random_choice([_ for _ in range(1000)], generator=rng)
            )
        self.assertEqual(len(set(random_choice_values)), 1)

        random_choice_2_values = []
        for _ in range(50):
            rng = np.random.default_rng(1)
            random_choice_2_values.extend(
                random_choice([_ for _ in range(1000)], size=3, generator=rng)
            )
        self.assertEqual(len(set(random_choice_2_values)), 3)
