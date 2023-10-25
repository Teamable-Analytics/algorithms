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

    def test_project_requirement_serializer__encodes_project_requirement_correctly(
        self,
    ):
        encoded_project_requirements = [
            json.dumps(pr, cls=ProjectRequirementSerializer)
            for pr in self.project_requirements
        ]
        self.assertEqual(self.json_project_requirements, encoded_project_requirements)

    def test_project_requirement_serializer__decode_returns_project_requirement(self):
        decoder = ProjectRequirementSerializer()
        decoded_project_requirement = decoder.decode(self.json_project_requirements[0])
        self.assertIsInstance(decoded_project_requirement, cls=ProjectRequirement)

    def test_project_requirement_serializer__decodes_project_requirements_correctly(
        self,
    ):
        decoder = ProjectRequirementSerializer()
        decoded_project_requirements = [
            decoder.decode(pr) for pr in self.json_project_requirements
        ]
        self.assertEqual(self.project_requirements, decoded_project_requirements)