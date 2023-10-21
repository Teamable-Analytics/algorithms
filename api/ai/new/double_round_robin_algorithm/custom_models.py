from api.models.project import Project
from api.models.student import Student


class Utility:
    def __init__(self, value: int, student: Student, project: Project):
        self.value = value
        self.student = student
        self.project = project

    def __lt__(self, other):
        # Reverse the order so that the highest utility is at the top of the heap
        return self.value > other.value
