from restructure.models.team_set import TeamSet
from restructure.simulations.evaluations.interfaces import TeamSetMetric
from restructure.simulations.evaluations.metrics.utils.team_calculations import (
    has_team_met_requirements,
)


class NumTeamsMeetingRequirements(TeamSetMetric):
    """
    The count of teams that have students that meet all of their requirements
    """

    def calculate(self, team_set: TeamSet) -> float:
        return sum([has_team_met_requirements(team) for team in team_set.teams])
