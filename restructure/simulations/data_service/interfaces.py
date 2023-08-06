from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict

from restructure.models.project import Project
from restructure.models.student import Student


@dataclass
class MockStudentProviderSettings:
    num_students: int
    num_friends_per_student: int
    num_enemies_per_student: int
    num_attributes: int
    num_requirements_to_match: int
    max_project_preferences_per_student: int


class ProjectProvider(ABC):

    @abstractmethod
    def get(self) -> List[Project]:
        raise NotImplementedError


class StudentProvider(ABC):

    @abstractmethod
    def get(self) -> List[Student]:
        raise NotImplementedError

    @property
    @abstractmethod
    def max_project_preferences_per_student(self) -> int:
        raise NotImplementedError
