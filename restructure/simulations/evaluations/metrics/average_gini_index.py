from restructure.models.team_set import TeamSet
from restructure.simulations.evaluations.interfaces import TeamSetMetric


class AverageGiniIndex(TeamSetMetric):

    @staticmethod
    def calculate(team_set: TeamSet):
        return 10  # todo: fix, obviously
