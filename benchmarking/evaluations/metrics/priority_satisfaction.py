from typing import List

from benchmarking.evaluations.interfaces import TeamSetMetric
from models.team_set import TeamSet


class PrioritySatisfaction(TeamSetMetric):
    def calculate(self, team_set: TeamSet) -> float:
        pass

    def compute_linear_weights(self, team_set: TeamSet) -> List[int]:
        pass
