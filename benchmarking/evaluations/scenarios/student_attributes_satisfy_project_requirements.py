from typing import List

from api.models.enums import DiversifyType, ScenarioAttribute, RequirementsCriteria
from benchmarking.evaluations.goals import (
    DiversityGoal,
    ProjectRequirementGoal,
)
from benchmarking.evaluations.interfaces import Goal, Scenario


class StudentAttributesSatisfyProjectRequirements(Scenario):
    @property
    def name(self) -> str:
        return "Meet Project Requirements, Project Preferences, and Diversify Gender"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(DiversifyType.DIVERSIFY, ScenarioAttribute.GENDER.value),
            ProjectRequirementGoal(
                criteria=RequirementsCriteria.STUDENT_ATTRIBUTES_ARE_RELEVANT
            ),
        ]
