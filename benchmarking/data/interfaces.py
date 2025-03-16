from abc import ABC, abstractmethod
from typing import List, Union, Tuple

from benchmarking.evaluations.enums import AttributeValueEnum
from api.dataclasses.student import Student
from api.dataclasses.team import TeamShell
from api.dataclasses.team_set import TeamSet

AttributeRangeConfig = Union[
    List[int],
    List[Tuple[int, float]],
    List[AttributeValueEnum],
    List[Tuple[AttributeValueEnum, float]],
]

NumValuesConfig = Union[int, Tuple[int, int]]


class TeamConfigurationProvider(ABC):
    @abstractmethod
    def get(self) -> TeamSet:
        """
        Returns a teamset. Primarily used as a convenient utility for returning a historical team <> student
        assignement that was retrieved from real-world data.

        i.e. "We want to see how the actual teams made from this real data set compare to the
            teamset that our algorithms generate"
        """
        raise NotImplementedError


class InitialTeamsProvider(ABC):
    @abstractmethod
    def get(self) -> List[TeamShell]:
        """
        Returns the shells of teams with requirements to be used in team generation.
        NOT to be used as a way to convert pre-existing team configuration data (as in, with students assigned)
            into a list of Team objects
        """
        raise NotImplementedError


class StudentProvider(ABC):
    @abstractmethod
    def get(self, seed: int = None) -> List[Student]:
        raise NotImplementedError

    @property
    @abstractmethod
    def num_students(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def max_project_preferences_per_student(self) -> int:
        raise NotImplementedError
