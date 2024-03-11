from api.dataclasses.student import Student


class Utility:
    def __init__(self, value: float, student: Student, project_id: int):
        self.value = value
        self.student = student
        self.project_id = project_id

    def __lt__(self, other):
        # Reverse the order so that the highest utility is at the top of the heap
        return self.value > other.value
