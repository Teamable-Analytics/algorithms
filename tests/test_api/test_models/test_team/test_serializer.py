import json
import unittest

from api.models.enums import RequirementOperator, Relationship
from api.models.project import ProjectRequirement
from api.models.student import Student
from api.models.team import Team, TeamSerializer


def are_students_equal_ignoring_team(s1: Student, s2: Student):
    for field_name in Student.__dataclass_fields__.keys():
        if field_name == "team":
            continue
        if s1.__getattribute__(field_name) != s2.__getattribute__(field_name):
            return False
    return True


def are_teams_equal_ignoring_students(t1: Team, t2: Team):
    for field_name in Team.__dataclass_fields__.keys():
        if field_name == "students":
            continue
        if t1.__getattribute__(field_name) != t2.__getattribute__(field_name):
            return False
    return True


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

        for team in cls.teams:
            for student in team.students:
                student.team = team

        json_students_team_1 = '[{"_id": 4, "name": "Teresa", "attributes": {"7": [2]}, "relationships": {"1": -1, "45": 1.1}, "project_preferences": [6]}, {"_id": 1, "name": "Sam", "attributes": {"1": [4, 5, 6]}, "relationships": {"100": 1.1, "45": 1.1, "1": 1.1}, "project_preferences": [4, 6]}]'
        json_requirements_team_1 = '[{"attribute": 4, "operator": "exactly", "value": 3}, {"attribute": 1, "operator": "less than", "value": 1}]'
        json_students_team_2 = '[{"_id": 45, "name": "James", "attributes": {}, "relationships": {}, "project_preferences": []}, {"_id": 46, "name": "Jessie", "attributes": {}, "relationships": {}, "project_preferences": []}, {"_id": 100, "name": "Meowth", "attributes": {}, "relationships": {}, "project_preferences": []}]'
        json_requirements_team_2 = (
            '[{"attribute": 2, "operator": "more than", "value": 6}]'
        )
        cls.json_teams = [
            f'{{"_id": 1, "name": "Team 1", "project_id": 6, "requirements": {json_requirements_team_1}, "students": {json_students_team_1}}}',
            f'{{"_id": 4, "name": "Team Rocket", "project_id": 4, "requirements": {json_requirements_team_2}, "students": {json_students_team_2}}}',
        ]

    def test_team_serializer__encodes_team_correctly_to_json(self):
        encoded_teams = [json.dumps(team, cls=TeamSerializer) for team in self.teams]
        self.assertEqual(self.json_teams, encoded_teams)

    def test_decode__returns_team(self):
        decoder = TeamSerializer()
        json_dict = json.loads(self.json_teams[0])
        decoded_team = decoder.decode(json_dict)
        self.assertIsInstance(decoded_team, cls=Team)

    def test_decode__students_returned_are_within_team(self):
        decoder = TeamSerializer()
        json_dict = json.loads(self.json_teams[0])
        decoded_team = decoder.decode(json_dict)

        for student in decoded_team.students:
            self.assertIsNotNone(student.team)
            self.assertIsInstance(student.team, Team)

    def test_team_serializer__decodes_teams_correctly_from_json(self):
        decoder = TeamSerializer()
        for i, team in enumerate(self.json_teams):
            json_dict = json.loads(team)
            decoded_team = decoder.decode(json_dict)

            # soft equality to avoid recursion depth error
            self.assertEqual(str(self.teams[i]), str(decoded_team))

            # a delicate approach to checking for deeper equality without causing the recursion depth error
            for s1, s2 in zip(decoded_team.students, self.teams[i].students):
                self.assertTrue(are_students_equal_ignoring_team(s1, s2))
                self.assertTrue(are_teams_equal_ignoring_students(s1.team, s2.team))
