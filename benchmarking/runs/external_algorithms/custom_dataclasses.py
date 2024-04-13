from enum import Enum

import math
from typing import List

from api.dataclasses.enums import AttributeValueEnum, RequirementOperator, Gpa
from api.dataclasses.project import Project, ProjectRequirement
from api.dataclasses.team import TeamShell
from benchmarking.data.interfaces import InitialTeamsProvider
from benchmarking.data.simulated_data.mock_initial_teams_provider import MockInitialTeamsProvider, \
    MockInitialTeamsProviderSettings


class ExternalAlgorithmScenarioAttribute(Enum):
    GPA = 100001
    NUMBER_OF_YEARS_CODING = 100002
    GIT_SKILL = 100003
    FE_DEVELOPMENT_SKILL = 100004
    BE_DEVELOPMENT_SKILL = 100005
    COMMUNICATION_SKILL = 100006


class ExternalAlgorithmDevelopmentSkill(AttributeValueEnum):
    NO_SKILL = 0
    BASIC_SKILL = 1
    INTERMEDIATE_SKILL = 2
    ADVANCED_SKILL = 3


class ExternalAlgorithmYearCoding(AttributeValueEnum):
    LESS_THAN_ONE_YEAR = 0
    ONE_YEAR = 1
    TWO_YEAR = 2
    MORE_THAN_TWO_YEARS = 3


class ExternalAlgorithmInitialTeamProvider(InitialTeamsProvider):
    def __init__(self, num_teams: int):
        super().__init__()

        TOTAL_PROJECTS = 4

        num_teams_per_project = math.ceil(num_teams / TOTAL_PROJECTS)

        # First project is a beginner-friendly project, require no experience, but avoid students with experience so they can work on better suited projects
        # Second project is a project that requires a bit of experience, but not too much, allow students with and without experience to join, but client is picky so need communication skill and not a D or below student
        # Third project is a serious project from a important client, requires a lot of experience, only allow students with experience and good GPA to join
        # Fourth project is a hard project but not as important as the third project, requires a lot of experience, but allow students with intermediate experience to join
        projects: List[Project] = [
            Project(
                _id=1,
                name="TODO List",
                number_of_teams=num_teams_per_project,
                requirements=[
                    ProjectRequirement(
                        attribute=ExternalAlgorithmScenarioAttribute.GIT_SKILL.value,
                        operator=RequirementOperator.LESS_THAN,
                        value=ExternalAlgorithmDevelopmentSkill.ADVANCED_SKILL.value,
                    ),
                    ProjectRequirement(
                        attribute=ExternalAlgorithmScenarioAttribute.NUMBER_OF_YEARS_CODING.value,
                        operator=RequirementOperator.LESS_THAN,
                        value=ExternalAlgorithmYearCoding.MORE_THAN_TWO_YEARS.value,
                    ),
                    ProjectRequirement(
                        attribute=ExternalAlgorithmScenarioAttribute.BE_DEVELOPMENT_SKILL.value,
                        operator=RequirementOperator.LESS_THAN,
                        value=ExternalAlgorithmDevelopmentSkill.ADVANCED_SKILL.value,
                    ),
                    ProjectRequirement(
                        attribute=ExternalAlgorithmScenarioAttribute.FE_DEVELOPMENT_SKILL.value,
                        operator=RequirementOperator.LESS_THAN,
                        value=ExternalAlgorithmDevelopmentSkill.ADVANCED_SKILL.value,
                    ),
                ],
            ),
            Project(
                _id=2,
                name="Blog Website",
                number_of_teams=num_teams_per_project,
                requirements=[
                    ProjectRequirement(
                        attribute=ExternalAlgorithmScenarioAttribute.COMMUNICATION_SKILL.value,
                        operator=RequirementOperator.MORE_THAN,
                        value=ExternalAlgorithmDevelopmentSkill.NO_SKILL.value,
                    ),
                    ProjectRequirement(
                        attribute=ExternalAlgorithmScenarioAttribute.GPA.value,
                        operator=RequirementOperator.MORE_THAN,
                        value=Gpa.D.value,
                    ),
                ],
            ),
            Project(
                _id=3,
                name="Redesign Government Website",
                number_of_teams=num_teams_per_project,
                requirements=[
                    ProjectRequirement(
                        attribute=ExternalAlgorithmScenarioAttribute.NUMBER_OF_YEARS_CODING.value,
                        operator=RequirementOperator.MORE_THAN,
                        value=ExternalAlgorithmYearCoding.TWO_YEAR.value,
                    ),
                    ProjectRequirement(
                        attribute=ExternalAlgorithmScenarioAttribute.GPA.value,
                        operator=RequirementOperator.MORE_THAN,
                        value=Gpa.B.value,
                    ),
                    ProjectRequirement(
                        attribute=ExternalAlgorithmScenarioAttribute.BE_DEVELOPMENT_SKILL.value,
                        operator=RequirementOperator.MORE_THAN,
                        value=ExternalAlgorithmDevelopmentSkill.BASIC_SKILL.value,
                    ),
                    ProjectRequirement(
                        attribute=ExternalAlgorithmScenarioAttribute.FE_DEVELOPMENT_SKILL.value,
                        operator=RequirementOperator.MORE_THAN,
                        value=ExternalAlgorithmDevelopmentSkill.BASIC_SKILL.value,
                    ),
                ],
            ),
            Project(
                _id=4,
                name="Create a Game",
                number_of_teams=num_teams_per_project,
                requirements=[
                    ProjectRequirement(
                        attribute=ExternalAlgorithmScenarioAttribute.NUMBER_OF_YEARS_CODING.value,
                        operator=RequirementOperator.MORE_THAN,
                        value=ExternalAlgorithmYearCoding.LESS_THAN_ONE_YEAR.value,
                    ),
                    ProjectRequirement(
                        attribute=ExternalAlgorithmScenarioAttribute.BE_DEVELOPMENT_SKILL.value,
                        operator=RequirementOperator.MORE_THAN,
                        value=ExternalAlgorithmDevelopmentSkill.BASIC_SKILL.value,
                    ),
                    ProjectRequirement(
                        attribute=ExternalAlgorithmScenarioAttribute.FE_DEVELOPMENT_SKILL.value,
                        operator=RequirementOperator.MORE_THAN,
                        value=ExternalAlgorithmDevelopmentSkill.BASIC_SKILL.value,
                    ),
                ],
            ),
        ]

        settings = MockInitialTeamsProviderSettings(
            projects=projects,
        )
        self.provider = MockInitialTeamsProvider(settings)

    def get(self) -> List[TeamShell]:
        return self.provider.get()
