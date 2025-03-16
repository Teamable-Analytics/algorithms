import collections
import unittest
from typing import Literal, List

import numpy as np

from algorithms.dataclasses.enums import Relationship
from benchmarking.evaluations.enums import Gpa
from algorithms.dataclasses.student import Student
from benchmarking.data.simulated_data.mock_student_provider import (
    create_mock_students,
    MockStudentProvider,
    random_choice,
    MockStudentProviderSettings,
    num_values_for_attribute,
    ProbabilisticAttributeValuesMaker,
    ExactAttributeRatiosMaker,
)
from algorithms.utils.validation import is_unique


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
            ensure_exact_attribute_ratios=False,
        )

        student = students[0]
        self.assertEqual(len(student.attributes[1]), 3)
        self.assertEqual(len(student.attributes[2]), 2)
        self.assertEqual(len(student.attributes[3]), 1)

    def test_create_mock_students__students_have_correct_project_preferences(self):
        for ensure_exact_attribute_ratios in [True, False]:
            students = create_mock_students(
                number_of_students=1,
                number_of_friends=0,
                number_of_enemies=0,
                friend_distribution="random",
                attribute_ranges={},
                num_values_per_attribute={},
                project_preference_options=[1, 2, 3],
                num_project_preferences_per_student=3,
                ensure_exact_attribute_ratios=ensure_exact_attribute_ratios,
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
            ensure_exact_attribute_ratios=False,
        )

        for student in students:
            self.assertTrue(2 <= len(student.attributes[1]) < 4)
            self.assertTrue(1 <= len(student.attributes[2]) < 3)
            self.assertTrue(3 <= len(student.attributes[3]) < 4)

    def test_create_mock_students__students_have_correct_friend_and_enemy_count(self):
        for ensure_exact_attribute_ratios in [True, False]:
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
                    ensure_exact_attribute_ratios=ensure_exact_attribute_ratios,
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
                ensure_exact_attribute_ratios=False,
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
                ensure_exact_attribute_ratios=False,
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
                ensure_exact_attribute_ratios=False,
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
                ensure_exact_attribute_ratios=False,
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
            ensure_exact_attribute_ratios=False,
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

    def test_create_mock_students__num_attributes_accurate(self):
        dist_types: List[Literal["random", "cluster"]] = ["random", "cluster"]
        for dist_type in dist_types:
            students = create_mock_students(
                number_of_students=4,
                number_of_friends=2,
                number_of_enemies=1,
                friend_distribution=dist_type,
                attribute_ranges={
                    1: [1, 2, 3, 4],
                    2: [(100, 0.5), (200, 0.5)],
                    3: [Gpa.A, Gpa.B, Gpa.C],
                    4: [(Gpa.A, 0.25), (Gpa.B, 0.5), (Gpa.C, 0.25)],
                    5: [1000],
                },
                num_values_per_attribute={
                    1: 2,
                    2: 0,  # explicitly setting 0 is allowed and enforced
                    3: [2, 3],
                    4: None,
                    # 5 skipped intentionally
                },
                project_preference_options=[],
                num_project_preferences_per_student=0,
                ensure_exact_attribute_ratios=False,
            )

            for student in students:
                self.assertEqual(2, len(student.attributes.get(1)))
                self.assertEqual(0, len(student.attributes.get(2)))
                self.assertTrue(len(student.attributes.get(3)) in [2, 3])
                self.assertEqual(1, len(student.attributes.get(4)))
                self.assertEqual(1, len(student.attributes.get(5)))

    def test_create_mock_students__students_are_reproducible(self):
        dist_types: List[Literal["random", "cluster"]] = ["random", "cluster"]
        for dist_type in dist_types:
            config = {
                "number_of_students": 4,
                "number_of_friends": 2,
                "number_of_enemies": 1,
                "friend_distribution": dist_type,
                "attribute_ranges": {
                    1: [1, 2, 3, 4],
                    2: [(100, 0.5), (200, 0.5)],
                    3: [Gpa.A, Gpa.B, Gpa.C],
                    4: [(Gpa.A, 0.25), (Gpa.B, 0.5), (Gpa.C, 0.25)],
                    5: [1000],
                },
                "num_values_per_attribute": {},
                "project_preference_options": [],
                "num_project_preferences_per_student": 0,
                "random_seed": 1,
                "ensure_exact_attribute_ratios": False,
            }

            students_1 = create_mock_students(**config)
            students_2 = create_mock_students(**config)
            students_3 = create_mock_students(**{**config, "random_seed": 2})

            self.assertListEqual(students_1, students_2)
            self.assertNotEqual(students_1, students_3)

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

    def test_random_choice__returns_correct_number_of_items(self):
        items = list(range(0, 100))
        values_1 = random_choice(possible_values=items, size=0)
        self.assertEqual(len(values_1), 0)

        values_2 = random_choice(possible_values=items, size=1)
        self.assertEqual(len(values_2), 1)

        values_3 = random_choice(possible_values=items, size=2)
        self.assertEqual(len(values_3), 2)

        values_4 = random_choice(possible_values=items, size=50)
        self.assertEqual(len(values_4), 50)

        values_5 = random_choice(possible_values=items, size=100)
        self.assertEqual(len(values_5), 100)

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


class TestProbabilisticAttributeValuesMaker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.attribute_ranges = {
            1: [1, 2, 3, 4],
            2: [(100, 0.5), (200, 0.25), (300, 0.25)],
            3: [Gpa.A, Gpa.B, Gpa.C],
            4: [(Gpa.A, 0.25), (Gpa.B, 0.5), (Gpa.C, 0.25)],
        }

    def test_get__errors_with_empty_range_config(self):
        maker = ProbabilisticAttributeValuesMaker(
            attribute_ranges=self.attribute_ranges
        )
        with self.assertRaises(Exception):
            maker.get(2000, num_values=1)

    def test_get__always_returns_correctly_sized_list(self):
        num_values_list = [1, 2, 3]
        maker = ProbabilisticAttributeValuesMaker(
            attribute_ranges=self.attribute_ranges
        )
        for num_values in num_values_list:
            for attribute_id in self.attribute_ranges.keys():
                self.assertEqual(
                    len(maker.get(attribute_id=attribute_id, num_values=num_values)),
                    num_values,
                )

    def test_get__multiple_values_for_attribute_are_selected_without_replacement(
        self,
    ):
        attribute_ranges = {
            1: [1, 2, 3],
            2: [(100, 0.5), (200, 0.25), (300, 0.25)],
            3: [Gpa.A, Gpa.B, Gpa.C],
            4: [(Gpa.A, 0.25), (Gpa.B, 0.5), (Gpa.C, 0.25)],
        }
        maker = ProbabilisticAttributeValuesMaker(attribute_ranges=attribute_ranges)
        for _ in range(100):
            # FIXME: This test is (technically) a little flaky 😬
            # run this multiple times so that this test cannot accidentally
            #   pass even if the values are selected with replacement
            values_1 = maker.get(1, num_values=3)
            self.assertListEqual([1, 2, 3], sorted(values_1))

            values_2 = maker.get(2, num_values=3)
            self.assertListEqual([100, 200, 300], sorted(values_2))

            values_3 = maker.get(3, num_values=3)
            self.assertListEqual(
                [Gpa.A.value, Gpa.B.value, Gpa.C.value], sorted(values_3)
            )

            values_4 = maker.get(4, num_values=3)
            self.assertListEqual(
                [Gpa.A.value, Gpa.B.value, Gpa.C.value], sorted(values_4)
            )

    def test_get__always_returns_list_of_integers(self):
        maker = ProbabilisticAttributeValuesMaker(
            attribute_ranges=self.attribute_ranges
        )
        for attribute_id in self.attribute_ranges.keys():
            value_list = maker.get(attribute_id=attribute_id, num_values=1)
            for value in value_list:
                self.assertIsInstance(value, int)


class TestExactAttributeRatiosMaker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.attribute_ranges = {
            1: [1, 2, 3, 4],
            2: [(100, 0.5), (200, 0.25), (300, 0.25)],
            3: [Gpa.A, Gpa.B, Gpa.C],
            4: [(Gpa.A, 0.25), (Gpa.B, 0.5), (Gpa.C, 0.25)],
        }
        cls.class_size = 100

    def test_get__errors_with_empty_range_config(self):
        maker = ExactAttributeRatiosMaker(
            number_of_students=self.class_size, attribute_ranges=self.attribute_ranges
        )
        with self.assertRaises(Exception):
            maker.get(2000, num_values=1)

    def test_get__always_returns_correctly_sized_list(self):
        maker = ExactAttributeRatiosMaker(
            number_of_students=self.class_size, attribute_ranges=self.attribute_ranges
        )
        for attribute_id in self.attribute_ranges.keys():
            self.assertEqual(len(maker.get(attribute_id=attribute_id, num_values=1)), 1)

    def test_init__exact_attribute_ratios_are_computed(self):
        NUM_RUN = 100  # Ensure probabilities are correct over many runs
        for _ in range(NUM_RUN):
            attribute_ranges = {
                1: [(100, 0.5), (200, 0.3), (300, 0.2)],
            }
            class_size = 100
            maker = ExactAttributeRatiosMaker(
                number_of_students=class_size, attribute_ranges=attribute_ranges
            )
            output_values = []
            for _ in range(class_size):
                value = maker.get(attribute_id=1, num_values=1)  # [100] | [200] | [300]
                output_values.extend(value)

            counter = collections.Counter(output_values)

            self.assertEqual(counter[100], 50)
            self.assertEqual(counter[200], 30)
            self.assertEqual(counter[300], 20)

    def test_get__always_returns_list_of_integers(self):
        maker = ExactAttributeRatiosMaker(
            number_of_students=self.class_size, attribute_ranges=self.attribute_ranges
        )
        for attribute_id in self.attribute_ranges.keys():
            value_list = maker.get(attribute_id=attribute_id, num_values=1)
            for value in value_list:
                self.assertIsInstance(value, int)
