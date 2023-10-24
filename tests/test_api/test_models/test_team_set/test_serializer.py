import unittest

from api.models.enums import RequirementOperator
from api.models.project import ProjectRequirement
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet


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
                    requirements=[
                        ProjectRequirement(
                            attribute=1, operator=RequirementOperator.LESS_THAN, value=1
                        )
                    ],
                    students=team_2_students,
                ),
            ],
        )
        json_student_1 = '{"_id": 4, "name": "Stevem", "attributes": {}, "relationships": {}, "project_preferences": []}'
        json_student_2 = '{"_id": 2, "name": "Hailey", "attributes": {}, "relationships": {}, "project_preferences": []}'
        json_student_3 = '{"_id": 3, "name": "Teamy Boi", "attributes": {}, "relationships": {}, "project_preferences": []}'
        json_project_requirement_1 = (
            '{"attribute": 1, "operator": "less than", "value": 1}'
        )
        json_team_1 = (
            '{"_id": 5, "name": "Team Numero 5", "requirements": [], "students": [%s, %s]}'
            % (json_student_1, json_student_2)
        )
        json_team_2 = (
            '{"_id": 2, "name": "Team 1", "project_id": 6, "requirements": [], "students": [%s, %s]}'
        )
        cls.json_team_set = (
            '{"_id": 421, "name": "Test Team Set", "teams": [{"_id": 5, name}]}'
        )
