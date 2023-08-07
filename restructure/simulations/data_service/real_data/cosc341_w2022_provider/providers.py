from typing import List

from restructure.models.student import Student
from restructure.models.team import Team
from restructure.simulations.data_service.interfaces import (
    StudentProvider,
    InitialTeamsProvider,
)


class COSC341W2022ProjectProvider(InitialTeamsProvider):
    def get(self) -> List[Team]:
        pass


class COSC341W2022StudentProvider(StudentProvider):
    def get(self) -> List[Student]:
        pass

    @property
    def max_project_preferences_per_student(self) -> int:
        return 1
