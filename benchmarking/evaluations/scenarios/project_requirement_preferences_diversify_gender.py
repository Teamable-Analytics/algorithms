from typing import List

from api.models.enums import DiversifyType, ScenarioAttribute
from benchmarking.evaluations.enums import PreferenceDirection, PreferenceSubject
from benchmarking.evaluations.goals import (
    DiversityGoal,
    WeightGoal,
    RequirementsCriteria,
    PreferenceGoal,
)
from benchmarking.evaluations.interfaces import Goal


class ProjectRequirementPreferenceDiversifyGender:
    @property
    def name(self) -> str:
        return "Meet Project Requirements, Project Preferences, and Diversify Gender"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(DiversifyType.DIVERSIFY, ScenarioAttribute.GENDER.value),
            RequirementsCriteria(),
            PreferenceGoal(
                direction=PreferenceDirection.INCLUDE,
                subject=PreferenceSubject.PROJECTS,
                max_project_preferences=3,
            ),
            WeightGoal(
                diversity_goal_weight=3,
                project_preference_weight=2,
                project_requirement_weight=1,
            ),
        ]
