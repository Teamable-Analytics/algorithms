from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from api.models.student import Student


@dataclass
class Priority(ABC):
    def __post_init__(self):
        self.validate()

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def satisfaction(self, students: List[Student]) -> float:
        # should always return a value in the range [0, 1]
        raise NotImplementedError