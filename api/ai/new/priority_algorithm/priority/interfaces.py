from abc import ABC, abstractmethod
from typing import List

from api.models.student import Student


class Priority(ABC):
    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def satisfied_by(self, students: List[Student]) -> bool:
        raise NotImplementedError
