from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.utils.team_calculations import num_satisfied_requirements


class NumRequirementsSatisfied(TeamSetMetric):
    """
    Across all teams, the number of requirements that have been satisfied.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calculate(self, team_set: TeamSet) -> float:
        return sum([num_satisfied_requirements(team) for team in team_set.teams])
