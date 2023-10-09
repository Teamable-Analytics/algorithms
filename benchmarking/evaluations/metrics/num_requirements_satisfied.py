from old.algorithm_sandbox.metrics.project_metric import satisfied_requirements
from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class NumRequirementsSatisfied(TeamSetMetric):
    """
    Across all teams, the number of requirements that have been satisfied.
    """

    def __init__(self, total_num_requirements: int, *args, **kwargs):
        min_value = 0
        max_value = total_num_requirements
        super().__init__(min_value, max_value, *args, **kwargs)

    def calculate(self, team_set: TeamSet) -> float:
        return sum([satisfied_requirements(team) for team in team_set.teams])
