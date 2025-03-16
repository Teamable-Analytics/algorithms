from old.algorithm_sandbox.metrics.project_metric import satisfied_requirements
from algorithms.dataclasses.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class NumRequirementsSatisfied(TeamSetMetric):
    """
    Across all teams, the number of requirements that have been satisfied.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calculate(self, team_set: TeamSet) -> float:
        return sum([satisfied_requirements(team) for team in team_set.teams])
