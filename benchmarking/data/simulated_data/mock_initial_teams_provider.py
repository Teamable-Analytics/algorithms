import copy
from dataclasses import dataclass
from typing import List

from benchmarking.data.interfaces import InitialTeamsProvider
from models.project import Project
from models.team import Team, TeamShell
from utils.validation import is_unique


@dataclass
class MockInitialTeamsProviderSettings:
    projects: List[Project] = None
    initial_teams: List[TeamShell] = None


class MockInitialTeamsProvider(InitialTeamsProvider):
    """
    Allows specification of a direct list of 'shell' teams OR a list of projects to be turned into 'shell' teams.
    Currently, NO support for specifying individual students that are already in a team.
    """

    def __init__(self, settings: MockInitialTeamsProviderSettings):
        if settings.initial_teams and settings.projects:
            raise ValueError("Please specify EITHER initial_teams OR projects.")
        if not settings.initial_teams and not settings.projects:
            raise ValueError("Either initial_teams OR projects must be specified.")

        if settings.projects and (
            not is_unique(settings.projects, attr="id")
            or not is_unique(settings.projects, attr="name")
        ):
            raise ValueError("Projects must have unique id and name fields.")
        if settings.initial_teams and (
            not is_unique(settings.initial_teams, attr="id")
            or not is_unique(settings.initial_teams, attr="name")
        ):
            raise ValueError("TeamShells must have unique id and name fields.")

        self.settings = settings

    def get(self) -> List[Team]:
        if self.settings.projects:
            return projects_to_teams(self.settings.projects)
        return team_shells_to_teams(self.settings.initial_teams)


def team_shells_to_teams(team_shells: List[TeamShell]) -> List[Team]:
    return [
        Team(
            _id=team_shell.id,
            name=team_shell.name,
            project_id=team_shell.project_id,
            requirements=copy.deepcopy(team_shell.requirements),
            is_locked=team_shell.is_locked,
        )
        for team_shell in team_shells
    ]


def projects_to_teams(projects: List[Project]) -> List[Team]:
    teams = []
    id_counter = 1  # start from 1
    for project in projects:
        for team_idx in range(project.number_of_teams):
            teams.append(
                Team(
                    _id=id_counter,
                    name=f"{project.name or f'Project {project.id}'} - {team_idx + 1}",
                    project_id=project.id,
                    requirements=copy.deepcopy(project.requirements),
                )
            )
            id_counter += 1

    return teams
