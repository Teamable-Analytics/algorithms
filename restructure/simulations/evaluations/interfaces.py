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
    @staticmethod
    @abstractmethod
    def calculate(team_set: TeamSet):
        raise NotImplementedError


@dataclass
class TokenizationConstraint:
    direction: TokenizationConstraintDirection
    threshold: int
    value: int  # todo: a bit iffy too
