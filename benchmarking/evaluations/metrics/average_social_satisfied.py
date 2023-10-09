from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class AverageSocialSatisfaction(TeamSetMetric):
    """
    Calculate the average social (friend/enemy) satisfaction among teams
    """

    def __init__(self, metric_function, num_teams: int, *args, **kwargs):
        min_value = 0
        max_value = 1  # Should be 1 assuming the input function has a bool return type
        super().__init__(min_value, max_value, *args, **kwargs)
        self.metric_function = metric_function

    def calculate(self, team_set: TeamSet) -> float:
        return (
            sum([self.metric_function(team) for team in team_set.teams])
            / team_set.num_teams
        )
