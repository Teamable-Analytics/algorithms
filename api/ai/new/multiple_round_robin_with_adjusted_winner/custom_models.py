from api.ai.new.multiple_round_robin_with_adjusted_winner.utils import calculate_value
from api.models.project import Project
from api.models.student import Student
from api.models.team import Team


class StudentProjectValue:
    def __init__(self, student: Student, project: Project):
        self.student = student
        self.project = project
        self.value = (
            0 if student.id < 0 else calculate_value(student, project.requirements)
        )

    def __lt__(self, other):
        # Redefine the less than operator to make it a max heap
        return self.value > other.value


class TeamWithValues(Team):
    project: Project

    def __init__(self, _id: int, project: Project):
        super().__init__(_id=_id)
        self.value = 0
        self.project = project
        self.requirements = project.requirements

    def add_student(self, student: Student) -> bool:
        if super().add_student(student):
            self.value += calculate_value(student, self.project.requirements)
            return True
        return False

    def remove_student(self, student: Student) -> bool:
        if student not in self.students:
            return False
        self.students.remove(student)
        self.value -= calculate_value(student, self.project.requirements)
        return True

    def __lt__(self, other):
        return self.value < other.value
