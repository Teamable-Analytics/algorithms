from json import JSONEncoder
from typing import Dict, Any

from api.models.project import ProjectRequirementSerializer
from api.models.serializer import JsonDecoder
from api.models.student import StudentSerializer
from api.models.team import Team


class TeamSerializer(JSONEncoder, JsonDecoder):
    def default(self, team: Team) -> Dict[str, any]:
        requirement_serializer = ProjectRequirementSerializer()
        student_serializer = StudentSerializer()
        requirements = [
            requirement_serializer.default(req) for req in team.requirements
        ]
        students = [student_serializer.default(student) for student in team.students]
        return {
            "_id": team._id,
            "name": team.name,
            "project_id": team.project_id,
            "requirements": requirements,
            "students": students,
        }

    def decode(self, json_dict: Dict[str, Any]) -> Team:
        requirement_serializer = ProjectRequirementSerializer()
        student_serializer = StudentSerializer()
        students = [student_serializer.decode(student) for student in json_dict["students"]]
        requirements = [
            requirement_serializer.decode(req) for req in json_dict["requirements"]
        ]
        return Team(
            _id=json_dict["_id"],
            name=json_dict["name"],
            project_id=json_dict["project_id"],
            requirements=requirements,
            students=students,
        )
