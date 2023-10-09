from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.utils.team_calculations import (
    has_team_met_requirements,
)


class NumTeamsMeetingRequirements(TeamSetMetric):
    """
    The count of teams that have students that meet all of their requirements
    """

    def __init__(self, num_teams: int, *args, **kwargs):
        min_value = 0
        max_value = num_teams
        super().__init__(min_value, max_value, *args, **kwargs)

    def calculate(self, team_set: TeamSet) -> float:
        return sum([has_team_met_requirements(team) for team in team_set.teams])
