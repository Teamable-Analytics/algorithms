import unittest

from api.models.student.student import Student
from utils.validation import is_unique


class TestValidationHelpers(unittest.TestCase):
    def test_validate_unique__works_with_primitives(self):
        self.assertTrue(is_unique([1, 2, 3]))
        self.assertFalse(is_unique([1, 2, 2]))
        self.assertTrue(is_unique(["A", "B"]))
        self.assertFalse(is_unique(["A", "A"]))

    def test_validate_unique__works_with_dictionaries(self):
        self.assertTrue(is_unique([{"id": 1}, {"id": 2}, {"id": 3}], attr="id"))
        self.assertFalse(is_unique([{"id": 1}, {"id": 1}, {"id": 1}], attr="id"))

    def test_validate_unique__works_with_classes(self):
        self.assertTrue(is_unique([Student(_id=1), Student(_id=2)], attr="id"))
        self.assertFalse(is_unique([Student(_id=1), Student(_id=1)], attr="id"))
