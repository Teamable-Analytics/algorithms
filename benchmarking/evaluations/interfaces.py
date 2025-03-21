from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional

from algorithms.dataclasses.team_set import TeamSet


@dataclass
class Goal(ABC):
    def __post_init__(self):
        self.validate()

    def validate(self):
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
        self,
        theoretical_range: Tuple[float, float] = None,
        name: str = None,
        *args,
        **kwargs
    ):
        self._name = name
        self._theoretical_range = theoretical_range

    @abstractmethod
    def calculate(self, team_set: TeamSet) -> float:
        raise NotImplementedError

    @property
    def theoretical_range(self) -> Optional[Tuple[float, float]]:
        if self._theoretical_range:
            return self._theoretical_range
        return None

    @property
    def name(self) -> str:
        if self._name:
            return self._name
        return self.__class__.__name__
