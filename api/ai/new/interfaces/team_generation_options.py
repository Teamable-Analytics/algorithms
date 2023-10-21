from dataclasses import dataclass
from typing import List

from schema import Schema

from api.models.team import TeamShell


@dataclass
class TeamGenerationOptions:
    max_team_size: int
    min_team_size: int
    total_teams: int
    # todo: add support for initial team options in new Algorithm structure
    initial_teams: List[TeamShell]

    def __post_init__(self):
        self.validate()

    def validate(self):
        Schema(int).validate(self.max_team_size)
        Schema(int).validate(self.min_team_size)
        Schema(int).validate(self.total_teams)
        if self.max_team_size < self.min_team_size:
            raise ValueError(
                f"max_team_size cannot be lower than min_team_size! ({self.max_team_size} < {self.min_team_size})"
            )
        if self.initial_teams:
            Schema([TeamShell]).validate(self.initial_teams)
            if len(self.initial_teams) != self.total_teams:
                raise ValueError(
                    f"team_options size ({len(self.initial_teams)}) != total_teams ({self.total_teams})"
                )
