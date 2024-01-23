from typing import List

from api.models.enums import RequirementsCriteria
from benchmarking.evaluations.goals import WeightGoal, ProjectRequirementGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class ProjectScenario(Scenario):
    @property
    def name(self) -> str:
        return "Project Scenario"

    @property
    def goals(self) -> List[Goal]:
        return [
            ProjectRequirementGoal(
                criteria=RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED
            ),
            WeightGoal(project_requirement_weight=1),
        ]
