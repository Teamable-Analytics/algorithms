import unittest

from api.models.enums import RequirementOperator
from api.models.project.project import ProjectRequirement
from api.models.project.project_requirement_serializer import ProjectRequirementSerializer


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
            '{"attribute": 1, "operator": "less than", "value": 2}'
        ]

    def test_project_requirement_serializer__encode_returns_dict(self):
        encoder = ProjectRequirementSerializer()
        project_requirement_encoded = encoder.encode()