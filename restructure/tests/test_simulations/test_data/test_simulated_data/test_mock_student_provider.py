import unittest

from restructure.simulations.data.simulated_data.mock_student_provider import (
    attribute_values_from_range,
)


class TestMockStudentProvider(unittest.TestCase):
    def test_attribute_values_from_range__errors_with_empty_range_config(self):
        with self.assertRaises(Exception):
            attribute_values_from_range([])
