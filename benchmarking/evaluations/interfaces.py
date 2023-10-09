from abc import ABC, abstractmethod
from typing import List

from api.models.team_set import TeamSet


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
    def __init__(
        self, min_value: float, max_value: float, name: str = None, *args, **kwargs
    ):
        self._name = name
        self._min_value = min_value
        self._max_value = max_value

    @abstractmethod
    def calculate(self, team_set: TeamSet) -> float:
        raise NotImplementedError

    @property
    def min_value(self) -> float:
        return self._min_value

    @property
    def max_value(self) -> float:
        return self._max_value

    @property
    def name(self) -> str:
        if self._name:
            return self._name
        return self.__class__.__name__
