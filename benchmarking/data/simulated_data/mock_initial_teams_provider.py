import copy
from dataclasses import dataclass
from typing import List

from benchmarking.data.interfaces import InitialTeamsProvider
from api.dataclasses.project import Project
from api.dataclasses.team import TeamShell
from api.utils.validation import is_unique


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

    def get(self) -> List[TeamShell]:
        if self.settings.projects:
            return projects_to_team_shells(self.settings.projects)
        return self.settings.initial_teams


def projects_to_team_shells(projects: List[Project]) -> List[TeamShell]:
    team_shells = []
    id_counter = 1  # start from 1
    for project in projects:
        for team_idx in range(project.number_of_teams):
            team_shells.append(
                TeamShell(
                    _id=id_counter,
                    name=f"{project.name or f'Project {project.id}'} - {team_idx + 1}",
                    project_id=project.id,
                    requirements=copy.deepcopy(project.requirements),
                )
            )
            id_counter += 1

    return team_shells
