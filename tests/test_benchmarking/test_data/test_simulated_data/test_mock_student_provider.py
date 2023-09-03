import unittest

from models.enums import Gpa, ScenarioAttribute, Relationship
from models.student import Student
from benchmarking.data.interfaces import MockStudentProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import (
    attribute_values_from_range, create_mock_students, MockStudentProvider,
)


class TestMockStudentProvider(unittest.TestCase):

    def test_get__returns_student_objects(self):
        students = MockStudentProvider(
            MockStudentProviderSettings(number_of_students=10)
        ).get()

        for student in students:
            self.assertIsInstance(student, Student)

    def test_max_project_preferences_are_correctly_inferred(self):
        max_project_preferences_1 = MockStudentProvider(
            MockStudentProviderSettings(
                number_of_students=10,
                attribute_ranges={
                    ScenarioAttribute.PROJECT_PREFERENCES.value: [1, 2, 3, 4],
                },
                num_values_per_attribute={
                    ScenarioAttribute.PROJECT_PREFERENCES.value: 3,
                }
            )
        ).max_project_preferences_per_student

        self.assertEqual(max_project_preferences_1, 3)

        max_project_preferences_2 = MockStudentProvider(
            MockStudentProviderSettings(
                number_of_students=10,
                attribute_ranges={
                    ScenarioAttribute.PROJECT_PREFERENCES.value: [1, 2, 3, 4],
                },
                num_values_per_attribute={
                    ScenarioAttribute.PROJECT_PREFERENCES.value: (1, 4),
                }
            )
        ).max_project_preferences_per_student

        self.assertEqual(max_project_preferences_2, 4)


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
        )

        student = students[0]
        self.assertEqual(len(student.attributes[1]), 3)
        self.assertEqual(len(student.attributes[2]), 2)
        self.assertEqual(len(student.attributes[3]), 1)

    def test_create_mock_students__student_has_num_values_for_attribute_within_range(self):
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
        )

        for student in students:
            self.assertTrue(2 <= len(student.attributes[1]) < 4)
            self.assertTrue(1 <= len(student.attributes[2]) < 3)
            self.assertTrue(3 <= len(student.attributes[3]) < 4)

    def test_create_mock_students__students_have_correct_friend_and_enemy_count(self):
        for i in [1, 5, 10]:
            students = create_mock_students(
                number_of_students=i + 1,
                number_of_friends=i,
                number_of_enemies=i,
                friend_distribution="random",
                attribute_ranges={},
                num_values_per_attribute={},
            )
            for student in students:
                self.assertGreaterEqual(i, len([r for r in student.relationships.values() if r == Relationship.FRIEND]))
                self.assertGreaterEqual(i, len([r for r in student.relationships.values() if r == Relationship.ENEMY]))

    def test_attribute_values_from_range__multiple_values_for_attribute_are_selected_without_replacement(self):
        for _ in range(100):
            # FIXME: This test is (technically) a little flaky 😬
            # run this multiple times so that this test cannot accidentally
            #   pass even if the values are selected with replacement
            values_1 = attribute_values_from_range([10, 20, 30], num_values=3)
            self.assertListEqual([10, 20, 30], sorted(values_1))

            values_2 = attribute_values_from_range([(10, 0.2), (20, 0.3), (30, 0.5)], num_values=3)
            self.assertListEqual([10, 20, 30], sorted(values_2))

            values_3 = attribute_values_from_range([Gpa.A, Gpa.B, Gpa.C], num_values=3)
            self.assertListEqual(sorted([Gpa.A.value, Gpa.B.value, Gpa.C.value]), sorted(values_3))

            values_4 = attribute_values_from_range([(Gpa.A, 0.2), (Gpa.B, 0.3), (Gpa.C, 0.5)], num_values=3)
            self.assertListEqual(sorted([Gpa.A.value, Gpa.B.value, Gpa.C.value]), sorted(values_4))

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
                len(attribute_values_from_range([10, 20, 30], num_values=num_values)),
                num_values,
            )
            self.assertEqual(
                len(attribute_values_from_range([(10, 0.2), (20, 0.3), (30, 0.5)], num_values=num_values)),
                num_values,
            )
            self.assertEqual(
                len(attribute_values_from_range([Gpa.A, Gpa.B, Gpa.C], num_values=num_values)),
                num_values,
            )
            self.assertEqual(
                len(attribute_values_from_range([(Gpa.A, 0.2), (Gpa.B, 0.3), (Gpa.C, 0.5)], num_values=num_values)),
                num_values,
            )

    def test_attribute_values_from_range__errors_with_empty_range_config(self):
        with self.assertRaises(Exception):
            attribute_values_from_range([])
