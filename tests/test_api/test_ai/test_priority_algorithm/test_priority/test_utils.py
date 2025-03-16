import unittest

from algorithms.ai.priority_algorithm.priority.utils import (
    student_attribute_binary_vector,
    int_dot_product,
    infer_possible_values,
)
from algorithms.dataclasses.student import Student


class TestPriorityUtils(unittest.TestCase):
    def test_student_attribute_binary_vector(self):
        possible_values = [100, 200, 300, 400, 500]
        attribute_id = 1

        self.assertListEqual(
            student_attribute_binary_vector(
                Student(_id=1, attributes={attribute_id: [100, 300, 500]}),
                attribute_id,
                possible_values,
            ),
            [1, 0, 1, 0, 1],
        )

        self.assertListEqual(
            student_attribute_binary_vector(
                Student(_id=1, attributes={attribute_id: [50]}),
                attribute_id,
                possible_values,
            ),
            [0, 0, 0, 0, 0],
        )

        self.assertListEqual(
            student_attribute_binary_vector(
                Student(_id=1, attributes={attribute_id: []}),
                attribute_id,
                possible_values,
            ),
            [0, 0, 0, 0, 0],
        )

    def test_int_dot_product(self):
        self.assertEqual(int_dot_product([0, 3, 1, 2], [2, 1, 4, 5]), 17)
        self.assertEqual(int_dot_product([0, 0, 0, 0], [21, 12, 4, 5]), 0)

    def test_infer_possible_values(self):
        attribute_id = 1
        students = [
            Student(_id=1, attributes={attribute_id: [10, 20]}),
            Student(_id=2, attributes={attribute_id: [30, 40, 50, 60]}),
            Student(_id=3, attributes={attribute_id: []}),
            Student(_id=3, attributes={attribute_id: [70]}),
        ]

        self.assertEqual(
            sorted(infer_possible_values(students, attribute_id)),
            [10, 20, 30, 40, 50, 60, 70],
        )
