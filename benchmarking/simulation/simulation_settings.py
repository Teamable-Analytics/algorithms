from dataclasses import dataclass

from benchmarking.data.interfaces import StudentProvider, InitialTeamsProvider
from benchmarking.evaluations.interfaces import Scenario
from api.utils.validation import assert_can_exist_together


@dataclass
class SimulationSettings:
    scenario: Scenario
    student_provider: StudentProvider
    num_teams: int = None
    min_team_size: int = None
    max_team_size: int = None
    initial_teams_provider: InitialTeamsProvider = None
    cache_key: str = None

    def __post_init__(self):
        self.validate()

    def validate(self):
        assert_can_exist_together(self.student_provider, self.initial_teams_provider)

        if self.initial_teams_provider and self.num_teams:
            raise ValueError(
                "Either specify num_teams OR give a project initial_teams_provider, not both."
            )
        if not self.num_teams and not self.initial_teams_provider:
            raise ValueError(
                "Either num_teams OR a project initial_teams_provider must be specified."
            )
        if (
            self.min_team_size
            and not self.max_team_size
            or self.max_team_size
            and not self.min_team_size
        ):
            raise ValueError("Both or neither min and max team size must be specified")
        if self.min_team_size:
            if self.min_team_size > self.max_team_size:
                raise ValueError("Min team size must be smaller than max team size")
            num_students = self.student_provider.num_students
            num_teams_local = self.num_teams or len(self.initial_teams_provider.get())
            min_students = num_teams_local * self.min_team_size
            if min_students > num_students:
                raise ValueError(
                    "The min team size is too big to fill all teams with the given students"
                )
            max_students = num_teams_local * self.max_team_size
            if max_students < num_students:
                raise ValueError(
                    "The max team size is too small to for all given students to fit into the teams"
                )
