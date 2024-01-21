from api.models.student import Student
from benchmarking.data.interfaces import StudentProvider


class CustomStudentProvider(StudentProvider):
    def __init__(self, num_students: int = 120, team_size: int = 4):
        super().__init__()
        self._num_students = num_students
        self.team_size = team_size

    @property
    def num_students(self) -> int:
        return self._num_students

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0

    def get_students(self):
        return [
            Student(
                _id=idx,
                attributes={
                    100: [idx, idx + 1],
                },
            ) for idx in range(self.num_students)
        ]
