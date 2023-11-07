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

    def test_encode__encodes_student_correctly_to_json(self):
        encoded_students = [
            json.dumps(student, cls=StudentSerializer) for student in self.students
        ]
        self.assertEqual(self.json_students, encoded_students)

    def test_decode__returns_student(self):
        decoder = StudentSerializer()
        json_dict = json.loads(self.json_students[0])
        decoded_student = decoder.decode(json_dict)
        self.assertIsInstance(decoded_student, cls=Student)

    def test_decode__decodes_student_correctly_from_json(self):
        decoder = StudentSerializer()
        for i, student in enumerate(self.json_students):
            json_dict = json.loads(student)
            decoded_student = decoder.decode(json_dict)
            self.assertEqual(self.students[i], decoded_student)
