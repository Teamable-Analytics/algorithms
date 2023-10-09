from typing import List

from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.utils.team_calculations import (
    team_gini_index,
)


class AverageGiniIndexMultiAttribute(TeamSetMetric):
    """
    Calculate the gini index for the given attributes for each team and average the results
    """

    def __init__(self, attributes: List[int], *args, **kwargs):
        min_value = 0
        max_value = 1
        super().__init__(min_value, max_value, *args, **kwargs)
        if attributes is None or len(attributes) == 0:
            raise ValueError("Must have at least one attribute")
        self.attributes = attributes

    def calculate(self, team_set: TeamSet) -> float:
        avg_sum = 0
        for attribute in self.attributes:
            avg_sum += (
                sum([team_gini_index(team, attribute) for team in team_set.teams])
                / team_set.num_teams
            )
        return avg_sum / len(self.attributes)
