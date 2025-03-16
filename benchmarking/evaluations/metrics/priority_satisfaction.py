import statistics
from typing import List

from algorithms.ai.priority_algorithm.priority.interfaces import Priority
from algorithms.dataclasses.team import Team
from algorithms.dataclasses.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class PrioritySatisfaction(TeamSetMetric):
    """
    Calculates the number of priorities satisfied by the algorithm
    """

    def __init__(
        self,
        priorities: List[Priority],
        is_linear: bool,
        exponent_base: int = 2,
        *args,
        **kwargs
    ):
        super().__init__(theoretical_range=(0, 1), *args, **kwargs)
        self.priorities = priorities
        self.is_linear = is_linear
        self.exponent_base = exponent_base

    def calculate(self, team_set: TeamSet) -> float:
        return statistics.mean(self.team_priority_satisfaction(team_set))

    def calculate_stdev(self, team_set: TeamSet) -> float:
        return statistics.stdev(self.team_priority_satisfaction(team_set))

    def compute_linear_weights(self) -> List[int]:
        k = len(self.priorities)
        weights = [k + 1 - i for i in range(1, k + 1)]
        return weights

    def computer_exponential_weights(self) -> List[float]:
        k = len(self.priorities)
        weights = [
            (self.exponent_base ** (k - i)) / ((self.exponent_base**k) - 1)
            for i in range(1, k + 1)
        ]
        return weights

    def priorities_satisfied(self, team: Team) -> List[float]:
        satisfied = [
            priority.satisfaction(team.students, team.to_shell())
            for priority in self.priorities
        ]
        return satisfied

    def team_priority_satisfaction(self, team_set: TeamSet) -> List[float]:
        weights = (
            self.compute_linear_weights()
            if self.is_linear
            else self.computer_exponential_weights()
        )
        scores = []
        theoretical_max = sum(range(1, len(self.priorities) + 1))
        for team in team_set.teams:
            priorities = self.priorities_satisfied(team)
            product = sum(w * p for w, p in zip(weights, priorities))
            if self.is_linear:
                # Need to also divide by the maximum possible score for linear ordered weights as they do not sum to one
                product /= theoretical_max
            scores.append(product)
        return scores
