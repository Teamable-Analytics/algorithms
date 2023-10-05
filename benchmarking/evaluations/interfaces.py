from abc import ABC, abstractmethod
from typing import List

from models.team_set import TeamSet


class Goal(ABC):
    pass


class Scenario(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def goals(self) -> List[Goal]:
        raise NotImplementedError


class TeamSetMetric(ABC):
    def __init__(self, name: str = None, *args, **kwargs):
        self._name = name

    @abstractmethod
    def calculate(self, team_set: TeamSet) -> float:
        raise NotImplementedError

    @property
    def name(self) -> str:
        if self._name:
            return self._name
        return self.__class__.__name__
