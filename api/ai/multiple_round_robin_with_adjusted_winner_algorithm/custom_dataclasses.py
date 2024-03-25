from typing import Callable

from api.dataclasses.student import Student
from api.dataclasses.team import Team, TeamShell


class StudentProjectValue:
    def __init__(
        self,
        student: Student,
        team: Team,
        utility_function: Callable[[Student, TeamShell], float],
    ):
        self.student = student
        self.value = utility_function(student, team.to_shell())

    def __lt__(self, other):
        # Redefine the less than operator to make it a max heap
        return self.value > other.value


class TeamWithValues(Team):
    def __init__(
        self, team: Team, utility_function: Callable[[Student, TeamShell], float]
    ):
        super().__init__(
            _id=team._id,
            students=team.students,
            requirements=team.requirements,
            project_id=team.project_id,
            name=team.name,
        )
        self.value = 0
        self.utility_function = utility_function

    def add_student(self, student: Student) -> bool:
        if super().add_student(student):
            self.value += self.utility_function(student, self.to_shell())
            return True
        return False

    def remove_student(self, student: Student) -> bool:
        if student not in self.students:
            return False
        self.students.remove(student)
        self.value -= self.utility_function(student, self.to_shell())
        return True

    def __lt__(self, other):
        return self.value < other.value
