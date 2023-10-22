import json
from json import JSONEncoder, JSONDecoder
from typing import Dict

from api.models.project import ProjectRequirementSerializer
from api.models.student import StudentSerializer
from api.models.team import Team


class TeamSerializer(JSONEncoder, JSONDecoder):
    def default(self, team: Team) -> Dict[str, any]:
        requirement_serializer = ProjectRequirementSerializer()
        student_serializer = StudentSerializer()
        requirements = [requirement_serializer.encode(req) for req in team.requirements]
        students = [student_serializer.encode(student) for student in team.students]
        return {
            "_id": team._id,
            "name": team.name,
            "project_id": team.project_id,
            "requirements": requirements,
            "is_locked": team.is_locked,
            "students": students,
        }

    def decode(self, s, _w=...):
        requirement_serializer = ProjectRequirementSerializer()
        student_serializer = StudentSerializer()
        data = json.loads(s)
        students = [student_serializer.decode(student) for student in data['students']]
        requirements = [requirement_serializer.decode(req) for req in data['requirements']]
        return Team(
            _id=data['_id'],
            name=data['name'],
            project_id=data['project_id'],
            is_locked=data['is_locked'],
            requirements=requirements,
            students=students
        )
