from typing import List
import numpy as np
from ai.priority_algorithm.interfaces import Priority
from benchmarking.evaluations.interfaces import TeamSetMetric
from models.team import Team
from models.team_set import TeamSet


class PrioritySatisfaction(TeamSetMetric):
    """
    Calculates the number of priorities satisfied by the algorithm
    """

    def __init__(self, priorities: List[Priority], is_linear: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.priorities = priorities
        self.is_linear = is_linear

    def calculate(self, team_set: TeamSet) -> float:
        weights = self.compute_linear_weights() if self.is_linear else self.computer_exponential_weights()
        return sum([
            np.multiply(weights, self.priorities_satisfied(team)) for team in TeamSet.teams
        ])

    def compute_linear_weights(self) -> List[int]:
        k = len(self.priorities)
        weights = [k + 1 - i for i in range(1, k + 1)]
        return weights

    def computer_exponential_weights(self) -> List[float]:
        k = len(self.priorities)
        weights = [(2 ** (k - 1)) / ((2 ** k) - 1) for i in range(1, k + 1)]
        return weights

    def priorities_satisfied(self, team: Team) -> List[int]:
        satisfied = [1 if priority.satisfied_by(team.students) else 0 for priority in self.priorities]
        return satisfied
