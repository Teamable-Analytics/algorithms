from models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.utils.team_calculations import (
    team_gini_index,
)


class AverageGiniIndexMultiAttribute(TeamSetMetric):
    """
    Calculate the gini index for the given attributes for each team and average the results
    """

    def __init__(self, attributes: list[int], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attributes = attributes

    def calculate(self, team_set: TeamSet) -> float:
        avg_sum = 0
        for attribute in self.attributes:
            avg_sum += (
                sum([team_gini_index(team, attribute) for team in team_set.teams])
                / team_set.num_teams
            )
        return avg_sum / len(self.attributes)
