from benchmarking.evaluations.metrics.utils.team_option import TeamOption
from models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class AverageSocialSatisfaction(TeamSetMetric):
    """
    Calculate the average social (friend/enemy) satisfaction among teams
    """

    def __init__(self, option: TeamOption, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.option = option

    def calculate(self, team_set: TeamSet) -> float:
        metric_function = self.option.get_function()
        return (
            sum([metric_function(team) for team in team_set.teams])
            / team_set.num_teams
        )
