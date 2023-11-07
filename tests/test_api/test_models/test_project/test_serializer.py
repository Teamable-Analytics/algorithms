import json
import unittest

from api.models.enums import RequirementOperator
from api.models.project import ProjectRequirement
from api.models.project import ProjectRequirementSerializer


class TestProjectRequirementSerializer(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.project_requirements = [
            ProjectRequirement(
                attribute=4, operator=RequirementOperator.EXACTLY, value=5
            ),
            ProjectRequirement(
                attribute=1, operator=RequirementOperator.LESS_THAN, value=2
            ),
        ]
        cls.json_project_requirements = [
            '{"attribute": 4, "operator": "exactly", "value": 5}',
            '{"attribute": 1, "operator": "less than", "value": 2}',
        ]

    def test_encode__encodes_project_requirement_correctly_to_json(
        self,
    ):
        encoded_project_requirements = [
            json.dumps(pr, cls=ProjectRequirementSerializer)
            for pr in self.project_requirements
        ]
        self.assertEqual(self.json_project_requirements, encoded_project_requirements)

    def test_decode__returns_project_requirement(self):
        decoder = ProjectRequirementSerializer()
        json_dict = json.loads(self.json_project_requirements[0])
        decoded_project_requirement = decoder.decode(json_dict)
        self.assertIsInstance(decoded_project_requirement, cls=ProjectRequirement)

    def test_decode__decodes_student_correctly_from_json(
        self,
    ):
        decoder = ProjectRequirementSerializer()
        for i, pr in enumerate(self.json_project_requirements):
            json_dict = json.loads(pr)
            decoded_pr = decoder.decode(json_dict)
            self.assertEqual(self.project_requirements[i], decoded_pr)
