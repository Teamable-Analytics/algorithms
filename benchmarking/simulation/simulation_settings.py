from dataclasses import dataclass

from benchmarking.data.interfaces import StudentProvider, InitialTeamsProvider
from benchmarking.evaluations.interfaces import Scenario
from utils.validation import assert_can_exist_together


@dataclass
class TeamGenerationSettings:
    num_teams: int = None
    min_team_size: int = None
    max_team_size: int = None
    initial_teams_provider: InitialTeamsProvider = None

    def validate(self, num_students: int):
        if self.initial_teams_provider and self.num_teams:
            raise ValueError("")
        if (
            self.min_team_size
            and not self.max_team_size
            or self.max_team_size
            and not self.min_team_size
        ):
            raise ValueError("Both or neither min and max team size is required")


@dataclass
class SimulationSettings:
    scenario: Scenario
    student_provider: StudentProvider
    team_generation_settings: TeamGenerationSettings
    cache_key: str = None

    def __post_init__(self):
        self.validate()

    def validate(self):
        if self.num_teams and self.initial_teams_provider:
            raise ValueError(
                "Either specify num_teams OR give a project initial_teams_provider, not both."
            )
        if not self.num_teams and not self.initial_teams_provider:
            raise ValueError(
                "Either num_teams OR a project initial_teams_provider must be specified."
            )
        assert_can_exist_together(self.student_provider, self.initial_teams_provider)

        self.team_generation_settings.validate(self.student_provider.num_students)
