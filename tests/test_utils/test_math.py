import unittest

from utils.math import change_range


class TestMathHelpers(unittest.TestCase):
    def test_change_range(self):
        self.assertEqual(0.5, change_range(2, (1, 3), (0, 1)))
        self.assertEqual(120, change_range(2, (0, 10), (100, 200)))

    def test_change_range__works_with_out_of_range(self):
        self.assertEqual(1.1, change_range(11, (0, 10), (0, 1)))
        self.assertEqual(-0.1, change_range(-1, (0, 10), (0, 1)))
