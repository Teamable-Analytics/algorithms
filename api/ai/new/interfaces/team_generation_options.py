from dataclasses import dataclass
from typing import List

from schema import Schema

from api.models.team import TeamShell
from utils.validation import is_unique


@dataclass
class TeamGenerationOptions:
    max_team_size: int
    min_team_size: int
    total_teams: int
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
            if not is_unique([t.id for t in self.initial_teams]):
                raise ValueError(f"Ids of team shells must be unique!")
            if len(self.initial_teams) > self.total_teams:
                raise ValueError(
                    f"team_options size ({len(self.initial_teams)}) > total_teams ({self.total_teams})"
                )
        project_requirements = {}
        for team in self.initial_teams:
            if team.project_id in project_requirements:
                if team.requirements != project_requirements[team.project_id]:
                    raise ValueError(
                        f"Teams with the same project id must have the same requirements!\n"
                        + f"(Expect {project_requirements[team.project_id]}, got {team.requirements})"
                    )
            else:
                project_requirements[team.project_id] = team.requirements
