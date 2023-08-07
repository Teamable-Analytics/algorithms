from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Literal, Union, Tuple

from restructure.models.student import Student
from restructure.models.team import Team


@dataclass
class MockStudentProviderSettings:
    number_of_students: int
    number_of_friends: int
    number_of_enemies: int
    friend_distribution: Literal["cluster", "random"]
    attribute_ranges: Dict[int, Union[List[int], List[Tuple[int, float]]]]


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
    def max_project_preferences_per_student(self) -> int:
        raise NotImplementedError
