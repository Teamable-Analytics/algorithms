from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from restructure.models.enums import TokenizationConstraintDirection
from restructure.models.team_set import TeamSet
from team_formation.app.team_generator.algorithm.algorithms import AlgorithmOptions


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
    @abstractmethod
    def calculate(self, team_set: TeamSet) -> float:
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__


@dataclass
class TokenizationConstraint:
    direction: TokenizationConstraintDirection
    threshold: int
    value: int
