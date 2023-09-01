from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Literal, Union, Tuple

from models.enums import AttributeValueEnum
from models.student import Student
from models.team import Team

AttributeRangeConfig = Union[
    List[int],
    List[Tuple[int, float]],
    List[AttributeValueEnum],
    List[Tuple[AttributeValueEnum, float]],
]

NumValuesConfig = Union[int, Tuple[int, int]]


@dataclass
class MockStudentProviderSettings:
    number_of_students: int
    attribute_ranges: Dict[int, AttributeRangeConfig] = field(default_factory=dict)
    num_values_per_attribute: Dict[int, NumValuesConfig] = field(default_factory=dict)
    number_of_friends: int = 0
    number_of_enemies: int = 0
    friend_distribution: Literal["cluster", "random"] = "random"


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
