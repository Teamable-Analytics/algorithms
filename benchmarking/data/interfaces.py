from abc import ABC, abstractmethod
from typing import List, Union, Tuple

from api.models.enums import AttributeValueEnum
from api.models.student.student import Student
from api.models.team import Team

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
