from dataclasses import dataclass
from typing import List

from benchmarking.data.interfaces import StudentProvider, InitialTeamsProvider
from benchmarking.evaluations.interfaces import Scenario, TeamSetMetric
from utils.validation import assert_can_exist_together


@dataclass
class SimulationSettings:
    scenario: Scenario
    student_provider: StudentProvider
    # todo: needed for now, will be removed when we separate metrics out
    metrics: List[TeamSetMetric]
    num_teams: int = None
    initial_teams_provider: InitialTeamsProvider = None

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
        if not self.metrics:
            raise ValueError("At least one metric must be specified for a simulation.")

        assert_can_exist_together(self.student_provider, self.initial_teams_provider)
