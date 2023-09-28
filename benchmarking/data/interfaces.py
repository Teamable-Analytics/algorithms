from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Literal, Union, Tuple

from models.enums import AttributeValueEnum
from models.project import Project
from models.student import Student
from models.team import Team, TeamShell

AttributeRangeConfig = Union[
    List[int],
    List[Tuple[int, float]],
    List[AttributeValueEnum],
    List[Tuple[AttributeValueEnum, float]],
]

NumValuesConfig = Union[int, Tuple[int, int]]


class InitialTeamsProvider(ABC):
    @abstractmethod
    def get(self) -> List[Team]:
        raise NotImplementedError


class StudentProvider(ABC):
    @abstractmethod
    def get(self) -> List[Student]:
        raise NotImplementedError

    @property
    @abstractmethod
    def num_students(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def max_project_preferences_per_student(self) -> int:
        raise NotImplementedError
