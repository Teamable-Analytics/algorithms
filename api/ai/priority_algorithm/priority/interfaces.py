from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from schema import Schema

from api.models.student import Student
from api.models.team import TeamShell


@dataclass
class Priority(ABC):
    def __post_init__(self):
        self.validate()

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def satisfaction(self, students: List[Student], team_shell: TeamShell) -> float:
        # should always return a value in the range [0, 1]
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_schema() -> Schema:
        raise NotImplementedError
