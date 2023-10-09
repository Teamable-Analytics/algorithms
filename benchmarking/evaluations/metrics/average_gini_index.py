from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.utils.team_calculations import (
    team_gini_index,
)


class AverageGiniIndex(TeamSetMetric):
    """
    Calculate the gini index for the given attribute for each team and average the results
    """

    def __init__(self, attribute: int, *args, **kwargs):
        min_value = 0
        max_value = 1
        super().__init__(min_value, max_value, *args, **kwargs)
        self.attribute = attribute

    def calculate(self, team_set: TeamSet) -> float:
        return (
            sum([team_gini_index(team, self.attribute) for team in team_set.teams])
            / team_set.num_teams
        )
