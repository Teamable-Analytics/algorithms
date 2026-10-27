from dataclasses import dataclass
from typing import List, Optional

from schema import Schema

from algorithms.dataclasses.team import TeamShell
from algorithms.utils.validation import is_unique


def get_team_size_error(
    num_students: int, num_teams: int, min_team_size: int, max_team_size: int
) -> Optional[str]:
    """
    Returns why the students cannot be split into num_teams teams of the allowed sizes, or None if they can.

    The algorithms always fill the smallest team next, so team sizes differ by at most one.
    Staying within these bounds therefore keeps every team between min_team_size and max_team_size.
    Without this check, students that do not fit are silently left out of the result.
    """
    if num_students > num_teams * max_team_size:
        return (
            f"{num_students} students do not fit into {num_teams} teams of at most {max_team_size} students "
            f"({num_students - num_teams * max_team_size} students would not be assigned to any team)."
        )
    if num_students < num_teams * min_team_size:
        return f"{num_students} students are not enough for {num_teams} teams of at least {min_team_size} students."
    return None


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
        if self.initial_teams:
            for team in self.initial_teams:
                if team.project_id in project_requirements:
                    if team.requirements != project_requirements[team.project_id]:
                        raise ValueError(
                            f"Teams with the same project id must have the same requirements!\n"
                            + f"(Expect {project_requirements[team.project_id]}, got {team.requirements})"
                        )
                else:
                    project_requirements[team.project_id] = team.requirements
