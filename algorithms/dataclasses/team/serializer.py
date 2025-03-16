from json import JSONEncoder
from typing import Dict, Any, List

from algorithms.dataclasses.project import ProjectRequirementSerializer, ProjectRequirement
from algorithms.dataclasses.interfaces import DataClassDecoder
from algorithms.dataclasses.student import StudentSerializer, Student
from algorithms.dataclasses.team import Team


class TeamSerializer(JSONEncoder, DataClassDecoder):
    def default(self, team: Team) -> Dict[str, any]:
        requirement_serializer = ProjectRequirementSerializer()
        student_serializer = StudentSerializer()
        requirements = [
            requirement_serializer.default(req) for req in team.requirements
        ]
        students = [student_serializer.default(student) for student in team.students]
        return {
            "id": team.id,
            "name": team.name,
            "project_id": team.project_id,
            "requirements": requirements,
            "students": students,
        }

    def decode(self, json_dict: Dict[str, Any]) -> Team:
        requirement_serializer = ProjectRequirementSerializer()
        student_serializer = StudentSerializer()
        students: List[Student] = [
            student_serializer.decode(student)
            for student in json_dict.get("students", [])
        ]
        requirements: List[ProjectRequirement] = [
            requirement_serializer.decode(req)
            for req in json_dict.get("requirements", [])
        ]
        team = Team(
            _id=int(json_dict.get("id", json_dict.get("_id"))),
            name=json_dict.get("name"),
            project_id=json_dict.get("project_id"),
            requirements=requirements,
            students=students,
        )

        for student in students:
            student.team = team
        return team
