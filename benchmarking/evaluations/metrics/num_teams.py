from api.dataclasses.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class NumberOfTeams(TeamSetMetric):
    def calculate(self, team_set: TeamSet) -> float:
        return len(team_set.teams)
