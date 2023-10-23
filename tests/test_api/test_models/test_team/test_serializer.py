import json
import unittest

from api.models.enums import RequirementOperator, Relationship
from api.models.project import ProjectRequirement
from api.models.student import Student
from api.models.team import Team, TeamSerializer


class TestTeamSerializer(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.teams = [
            Team(
                _id=1,
                name="Team 1",
                project_id=6,
                requirements=[
                    ProjectRequirement(
                        attribute=4, operator=RequirementOperator.EXACTLY, value=3
                    ),
                    ProjectRequirement(
                        attribute=1, operator=RequirementOperator.LESS_THAN, value=1
                    ),
                ],
                students=[
                    Student(
                        _id=4,
                       name="Teresa",
                        attributes={7: [2]},
                        relationships={1: Relationship.FRIEND, 45: Relationship.ENEMY},
                        project_preferences=[6],
                    ),
                    Student(
                        _id=1,
                        name="Sam",
                        attributes={1: [4, 5, 6]},
                        relationships={
                            100: Relationship.ENEMY,
                            45: Relationship.ENEMY,
                            1: Relationship.ENEMY,
                        },
                        project_preferences=[4, 6],
                    ),
                ],
            ),
            Team(
                _id=4,
                name="Team Rocket",
                project_id=4,
                requirements=[
                    ProjectRequirement(
                        attribute=2, operator=RequirementOperator.MORE_THAN, value=6
                    )
                ],
                students=[
                    Student(_id=45, name="James"),
                    Student(_id=46, name="Jessie"),
                    Student(_id=100, name="Meowth"),
                ],
            ),
        ]
        json_students_team_1 = '[{"_id": 4, "name": "Teresa", "attributes": {"7": [2]}, "relationships": {"1": -1, "45": 1.1}, "project_preferences": [6]}, {"_id": 1, "name": "Sam", "attributes": {"1": [4, 5, 6]}, "relationships": {"100": 1.1, "45": 1.1, "1": 1.1}, "project_preferences": [4, 6]}]'
        json_requirements_team_1 = '[{"attribute": 4, "operator": "exactly", "value": 3}, {"attribute": 1, "operator": "less than", "value": 1}]'
        json_students_team_2 = '[{"_id": 45, "name": "James", "attributes": {}, "relationships": {}, "project_preferences": []}, {"_id": 46, "name": "Jessie", "attributes": {}, "relationships": {}, "project_preferences": []}, {"_id": 100, "name": "Meowth", "attributes": {}, "relationships": {}, "project_preferences": []}]'
        json_requirements_team_2 = '[{"attribute": 2, "operator": "more than", "value": 6}]'
        cls.json_teams = [
            '{"_id": 1, "name": "Team 1", "project_id": 6, "requirements": %s, "students": %s}'
            % (json_requirements_team_1, json_students_team_1),
            '{"_id": 4, "name": "Team Rocket", "project_id": 4, "requirements": %s, "students": %s}'
            % (json_requirements_team_2, json_students_team_2)
        ]

    def test_team_serializer__encodes_team_correctly(self):
        encoded_teams = [json.dumps(team, cls=TeamSerializer) for team in self.teams]
        self.assertEqual(self.json_teams, encoded_teams)

    def test_team_serializer__decode_returns_team(self):
        decoder = TeamSerializer()
        decoded_team = decoder.decode(s=self.json_teams[0])
        self.assertIsInstance(decoded_team, cls=Team)

    def test_team_serializer__decodes_teams_correctly(self):
        decoder = TeamSerializer()
        decoded_teams = [decoder.decode(team) for team in self.json_teams]
        self.assertEqual(self.teams, decoded_teams)
