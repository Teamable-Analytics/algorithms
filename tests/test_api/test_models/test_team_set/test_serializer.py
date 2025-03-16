import json
import unittest

from algorithms.dataclasses.enums import RequirementOperator
from algorithms.dataclasses.project import ProjectRequirement
from algorithms.dataclasses.student import Student
from algorithms.dataclasses.team import Team
from algorithms.dataclasses.team_set import TeamSet
from algorithms.dataclasses.team_set.serializer import TeamSetSerializer


class TestTeamSetSerializer(unittest.TestCase):
    @classmethod
    def setUp(cls):
        team_1_students = [Student(_id=1, name="Steven"), Student(_id=2, name="Hailey")]
        team_2_students = [Student(_id=3, name="Teamy Boi")]
        cls.team_set = TeamSet(
            _id=421,
            name="Test Team Set",
            teams=[
                Team(_id=5, name="Team Numero 5", students=team_1_students),
                Team(
                    _id=2,
                    name="Goosed",
                    project_id=11,
                    requirements=[
                        ProjectRequirement(
                            attribute=1, operator=RequirementOperator.LESS_THAN, value=1
                        )
                    ],
                    students=team_2_students,
                ),
            ],
        )
        json_student_1 = '{"id": 1, "name": "Steven", "attributes": {}, "relationships": {}, "project_preferences": []}'
        json_student_2 = '{"id": 2, "name": "Hailey", "attributes": {}, "relationships": {}, "project_preferences": []}'
        json_student_3 = '{"id": 3, "name": "Teamy Boi", "attributes": {}, "relationships": {}, "project_preferences": []}'
        json_project_requirement_team_2 = (
            '{"attribute": 1, "operator": "less than", "value": 1}'
        )

        json_team_1 = f'{{"id": 5, "name": "Team Numero 5", "project_id": null, "requirements": [], "students": [{json_student_1}, {json_student_2}]}}'
        json_team_2 = f'{{"id": 2, "name": "Goosed", "project_id": 11, "requirements": [{json_project_requirement_team_2}], "students": [{json_student_3}]}}'
        cls.json_team_set = f'{{"id": 421, "name": "Test Team Set", "teams": [{json_team_1}, {json_team_2}]}}'

    def test_team_serializer__encodes_team_set_correctly_to_json(self):
        encoded_team_set = json.dumps(self.team_set, cls=TeamSetSerializer)
        self.assertEqual(self.json_team_set, encoded_team_set)

    def test_decode__returns_team_set(self):
        decoder = TeamSetSerializer()
        json_dict = json.loads(self.json_team_set)
        decoded_team_set = decoder.decode(json_dict)
        self.assertIsInstance(decoded_team_set, cls=TeamSet)

    def test_team_serializer__decodes_teams_correctly_from_json(self):
        decoder = TeamSetSerializer()
        json_dict = json.loads(self.json_team_set)
        decoded_team_set = decoder.decode(json_dict)
        self.assertEqual(self.team_set, decoded_team_set)
