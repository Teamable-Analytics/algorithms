from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class EnvyFreeUpToOne(TeamSetMetric):
    """
    Calculate the envy-free up to one metric for the given attribute for each team and average the results

    A allocation is envy-free up to one if no agent envies another agent by more than one unit of the given attribute
    Meaning if A is envying B, then A will no longer envy B if we remove one unit of the given attribute from  B
    """

    def __init__(self, attribute: int, *args, **kwargs):
        super().__init__("EF1", *args, **kwargs)
        self.attribute = attribute

    def calculate(self, team_set: TeamSet) -> float:
        pass
