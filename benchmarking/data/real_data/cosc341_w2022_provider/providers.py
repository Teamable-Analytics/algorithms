from typing import List

from api.models.student import Student
from api.models.team import Team
from benchmarking.data.interfaces import (
    StudentProvider,
    InitialTeamsProvider,
)


class COSC341W2022InitialTeamsProvider(InitialTeamsProvider):
    def get(self) -> List[Team]:
        pass


class COSC341W2022StudentProvider(StudentProvider):
    def get(self, seed: int = None) -> List[Student]:
        pass

    @property
    def num_students(self) -> int:
        return 1

    @property
    def max_project_preferences_per_student(self) -> int:
        return 1
