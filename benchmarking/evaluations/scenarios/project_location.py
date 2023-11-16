from typing import List

from api.models.enums import DiversifyType, ScenarioAttribute
from benchmarking.evaluations.goals import (
    DiversityGoal,
    WeightGoal,
    RequirementsCriteria,
)
from benchmarking.evaluations.interfaces import Scenario, Goal


class ProjectLocation(Scenario):
    @property
    def name(self) -> str:
        return "Concentrate Individuals on Location and Meeting Project Requirements"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(DiversifyType.CONCENTRATE, ScenarioAttribute.LOCATION.value),
            RequirementsCriteria(),
            WeightGoal(diversity_goal_weight=2, project_requirement_weight=1),
        ]
