from typing import List

from api.dataclasses.enums import RequirementsCriteria
from benchmarking.evaluations.goals import WeightGoal, ProjectRequirementGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class SatisfyProjectRequirements(Scenario):
    @property
    def name(self) -> str:
        return "Satisfy Project Requirements"

    @property
    def goals(self) -> List[Goal]:
        return [
            ProjectRequirementGoal(),
            WeightGoal(project_requirement_weight=1),
        ]
