from functools import cached_property
from typing import Dict, List

from api.models.enums import ScenarioAttribute, Location
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProviderSettings,
)
from benchmarking.evaluations.interfaces import Scenario, TeamSetMetric
from benchmarking.evaluations.metrics.num_teams_meeting_requirements import (
    NumTeamsMeetingRequirements,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.project_location import ProjectLocation
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.interfaces import PriorityAlgorithmBenchmark
from benchmarking.simulation.goal_to_priority import goals_to_priorities


class ProjectLocationPriorityAlgorithmBenchmark(PriorityAlgorithmBenchmark):
    RATIO_OF_VANCOUVER_STUDENTS = 0.5

    @property
    def graph_dicts(self) -> List[Dict]:
        graph_runtime_dict = {}
        graph_num_reqs_met = {}
        graph_priority_dict = {}
        return [
            graph_runtime_dict,
            graph_num_reqs_met,
            graph_priority_dict,
        ]

    @property
    def metrics(self) -> Dict[str, TeamSetMetric]:
        return {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(self.scenario.goals),
                False,
            ),
            "NumTeamsMeetingRequirements": NumTeamsMeetingRequirements(),
        }

    def mock_student_provider_settings(self, **kwargs):
        return MockStudentProviderSettings(
            number_of_students=kwargs.get(
                "number_of_students", self.NUMBER_OF_STUDENTS
            ),
            attribute_ranges={
                ScenarioAttribute.LOCATION.value: [
                    (Location.Okanagan, 1 - self.RATIO_OF_VANCOUVER_STUDENTS),
                    (Location.Vancouver, self.RATIO_OF_VANCOUVER_STUDENTS),
                ],
            },
        )

    @cached_property
    def scenario(self) -> Scenario:
        return ProjectLocation()
