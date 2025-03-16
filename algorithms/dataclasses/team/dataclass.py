from dataclasses import dataclass, field
from typing import List, Dict

from algorithms.dataclasses.project import ProjectRequirement
from algorithms.dataclasses.student import Student


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

    def num_requirements_met_by_student(self, student: "Student") -> int:
        return sum(
            [
                int(requirement.met_by_student(student))
                for requirement in self.requirements
            ]
        )

    def lock(self):
        self.is_locked = True

    def unlock(self):
        self.is_locked = False


@dataclass
class Team(TeamShell):
    students: List[Student] = field(default_factory=list)

    def __post_init__(self):
        # if this team is initialized with students, all students have their .team assigned properly
        for s in self.students:
            s.team = self

    def __eq__(self, other):
        from utils.equality import teams_are_equal

        return teams_are_equal(self, other)

    @property
    def size(self) -> int:
        return len(self.students)

    @classmethod
    def from_shell(cls, shell: TeamShell) -> "Team":
        name = shell.name or f"Team {shell.id}"
        return cls(
            _id=shell.id,
            name=name,
            project_id=shell.project_id,
            requirements=shell.requirements,
            is_locked=shell.is_locked,
        )

    def to_shell(self) -> TeamShell:
        return TeamShell(
            _id=self.id,
            name=self.name,
            project_id=self.project_id,
            requirements=self.requirements,
            is_locked=self.is_locked,
        )

    def empty(self):
        for student in self.students:
            student.team = None
        self.students = []

    def add_student(self, student: "Student"):
        if self.is_locked:
            raise ValueError(f"Cannot add student ({student.id}) to team {self.id}.")
        self.students.append(student)

    def remove_student(self, student_to_remove: "Student"):
        if self.is_locked:
            raise ValueError(
                f"Cannot remove student ({student_to_remove.id}) from team {self.id}."
            )
        self.students.remove(student_to_remove)

    def todict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "student_ids": [student.id for student in self.students],
            "project_id": self.project_id,
        }
