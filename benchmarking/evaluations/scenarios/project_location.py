from typing import List

from api.dataclasses.enums import DiversifyType, ScenarioAttribute, RequirementsCriteria
from benchmarking.evaluations.goals import (
    DiversityGoal,
    WeightGoal,
    ProjectRequirementGoal,
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
            ProjectRequirementGoal(
                criteria=RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED
            ),
            WeightGoal(diversity_goal_weight=2, project_requirement_weight=1),
        ]
