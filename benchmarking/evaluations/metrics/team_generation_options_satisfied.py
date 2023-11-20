from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class TeamGenerationOptionsSatisfied(TeamSetMetric):
    def __init__(self, options: TeamGenerationOptions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = options

    def calculate(self, team_set: TeamSet) -> float:
        return sum([
            float(self.options.max_team_size >= len(team.students) >= self.options.min_team_size)
            for team in team_set.teams
        ]) / len(team_set.teams)
