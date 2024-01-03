from typing import List

from api.models.enums import RequirementsCriteria
from benchmarking.evaluations.goals import ProjectRequirementGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class StudentAttributesSatisfyProjectRequirements(Scenario):
    @property
    def name(self) -> str:
        return "Student Attributes Satisfy Project Requirements"

    @property
    def goals(self) -> List[Goal]:
        return [
            ProjectRequirementGoal(
                criteria=RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED
            )
        ]
