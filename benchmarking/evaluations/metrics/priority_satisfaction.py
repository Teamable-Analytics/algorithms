from typing import List

from api.ai.priority_algorithm.interfaces import Priority
from api.models.team import Team
from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class PrioritySatisfaction(TeamSetMetric):
    """
    Calculates the number of priorities satisfied by the algorithm
    """

    def __init__(self, priorities: List[Priority], is_linear: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.priorities = priorities
        self.is_linear = is_linear

    def calculate(self, team_set: TeamSet) -> float:
        weights = (
            self.compute_linear_weights()
            if self.is_linear
            else self.computer_exponential_weights()
        )
        total_score = 0
        for team in team_set.teams:
            priorities = self.priorities_satisfied(team)
            product = sum(w * p for w, p in zip(weights, priorities))
            total_score += product
        return total_score

    def compute_linear_weights(self) -> List[int]:
        k = len(self.priorities)
        weights = [k + 1 - i for i in range(1, k + 1)]
        return weights

    def computer_exponential_weights(self) -> List[float]:
        k = len(self.priorities)
        weights = [(2 ** (k - i)) / ((2**k) - 1) for i in range(1, k + 1)]
        return weights

    def priorities_satisfied(self, team: Team) -> List[int]:
        satisfied = [
            1 if priority.satisfied_by(team.students) else 0
            for priority in self.priorities
        ]
        return satisfied
