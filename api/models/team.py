from dataclasses import dataclass, field
from typing import List

from api.models.project import ProjectRequirement
from api.models.student import Student


@dataclass
class TeamShell:
    """
    Refers to a team that has no students, but can have requirements.
    Note: 'shell' teams are how the algorithms work, even when you have projects, their requirements are copied into N
        'shell' teams so the algorithms can understand them.
    """

    _id: int
    name: str = None
    project_id: int = None
    requirements: List[ProjectRequirement] = field(default_factory=list)
    is_locked: bool = False

    @property
    def id(self) -> int:
        return self._id


@dataclass
class Team(TeamShell):
    students: List[Student] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.students)

    def empty(self):
        for student in self.students:
            student.team = None
        self.students = []

    def add_student(self, student: "Student"):
        if self.is_locked or student.team is not None:
            return False
        self.students.append(student)
        return True

    def to_json(self):
        return {
            "students": [student.to_json() for student in self.students],
        }
