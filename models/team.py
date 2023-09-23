from dataclasses import dataclass, field
from typing import List

from models.project import ProjectRequirement
from models.student import Student


@dataclass
class Team:
    _id: int
    name: str = None
    project_id: int = None
    students: List[Student] = field(default_factory=list)
    requirements: List[ProjectRequirement] = field(default_factory=list)
    is_locked: bool = False

    @property
    def id(self) -> int:
        return self._id

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
