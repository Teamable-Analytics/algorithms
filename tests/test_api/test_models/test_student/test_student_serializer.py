import json
import unittest

from api.models.enums import Relationship
from api.models.student import Student, StudentSerializer


class TestStudentSerializer(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.students = [
            Student(
                _id=1,
                name="Harry",
                attributes={4: [2, 56, 1], 11: [2], 234: [-1, 0]},
                relationships={2: Relationship.FRIEND},
                project_preferences=[6, 1],
            ),
            Student(
                _id=2,
                name="Jane",
                attributes={4: [31, 2], 11: [], 234: [1, -1]},
                relationships={1: Relationship.FRIEND},
                project_preferences=[3, 2],
            ),
        ]
        cls.json_students = [
            '{"_id": 1, "name": "Harry", "attributes": {"4": [2, 56, 1], "11": [2], "234": [-1, 0]}, "relationships": {"2": -1}, "project_preferences": [6, 1]}',
            '{"_id": 2, "name": "Jane", "attributes": {"4": [31, 2], "11": [], "234": [1, -1]}, "relationships": {"1": -1}, "project_preferences": [3, 2]}',
        ]

    def test_student_serializer__encodes_students_correctly(self):
        encoded_students = [
            json.dumps(student, cls=StudentSerializer) for student in self.students
        ]
        self.assertEqual(self.json_students, encoded_students)

    def test_student_serializer__decode_returns_student(self):
        decoder = StudentSerializer()
        decoded_student = decoder.decode(s=self.json_students[0])
        self.assertIsInstance(decoded_student, cls=Student)

    def test_student_serializer__decodes_students_correctly(self):
        decoder = StudentSerializer()
        decoded_students = [decoder.decode(s=student) for student in self.json_students]
        self.assertEqual(self.students, decoded_students)
