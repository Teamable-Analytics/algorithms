from dataclasses import dataclass
from typing import List, Dict

from schema import Schema

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet, PriorityTeam
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.dataclasses.student import Student
from api.dataclasses.team import TeamShell, Team


@dataclass
class EvenPriority(Priority):
    """
    A mock priority to check that all students in a team have an even student id
    """

    def satisfaction(self, students: List[Student], team_shell: TeamShell) -> float:
        for student in students:
            if student.id % 2 == 1:
                return 0
        return 1

    def validate(self) -> bool:
        return True

    @staticmethod
    def get_schema() -> Schema:
        return Schema({})

    @staticmethod
    def parse_json(data: Dict) -> "Priority":
        return EvenPriority()


@dataclass
class LooseEvenPriority(Priority):
    """
    A mock priority to check that a student in a team have an even student id
    """

    def satisfaction(self, students: List[Student], team_shell: TeamShell) -> float:
        for student in students:
            if student.id % 2 == 0:
                return 1
        return 0

    def validate(self) -> bool:
        return True

    @staticmethod
    def get_schema() -> Schema:
        return Schema({})

    @staticmethod
    def parse_json(data: Dict) -> "Priority":
        return LooseEvenPriority()


@dataclass
class JohnPriority(Priority):
    """
    A mock priority that checks if a team has a student named John
    """

    def satisfaction(self, students: List[Student], team_shell: TeamShell) -> float:
        for student in students:
            if student.name == "John":
                return 1
        return 0

    def validate(self) -> bool:
        return True

    @staticmethod
    def get_schema() -> Schema:
        return Schema({})

    @staticmethod
    def parse_json(data: Dict) -> "Priority":
        return JohnPriority()


def get_mock_students():
    return [
        Student(_id=1, name="Joe"),
        Student(_id=2, name="John"),
        Student(_id=3, name=""),
        Student(_id=4, name="123"),
    ]


def get_mock_students_v2():
    return [
        Student(_id=1, name="John"),
        Student(_id=3, name="John"),
        Student(_id=2, name="Joe"),
        Student(_id=4, name="123"),
    ]


def get_mock_student_dict(students: List[Student]):
    student_dict = {}
    for student in students:
        student_dict[student.id] = student
    return student_dict


def get_mock_team_set(students: List[Student]):
    teams = [
        Team(_id=1, name="Team 1", students=students[0:2]),
        Team(_id=2, name="Team 2", students=students[2:4]),
    ]
    return PriorityTeamSet(
        [
            PriorityTeam(team, [student.id for student in team.students])
            for team in teams
        ]
    )
