from dataclasses import dataclass


@dataclass
class TeamGenerationOptions:
    max_team_size: int
    min_team_size: int
    total_teams: int
    team_options: list

    def __post_init__(self):
        self.validate()

    def validate(self):
        raise NotImplementedError
