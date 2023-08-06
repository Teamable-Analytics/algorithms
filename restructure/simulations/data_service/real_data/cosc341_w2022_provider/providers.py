from typing import List

from restructure.models.project import Project
from restructure.models.student import Student
from restructure.simulations.data_service.interfaces import (
    StudentProvider,
    ProjectProvider,
)


class COSC341W2022ProjectProvider(ProjectProvider):
    def get(self) -> List[Project]:
        pass


class COSC341W2022StudentProvider(StudentProvider):
    def get(self) -> List[Student]:
        pass

    @property
    def max_project_preferences_per_student(self) -> int:
        return 1
