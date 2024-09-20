from typing import List

from api.dataclasses.enums import DiversifyType, ScenarioAttribute, RequirementsCriteria
from benchmarking.evaluations.enums import PreferenceDirection, PreferenceSubject
from benchmarking.evaluations.goals import (
    DiversityGoal,
    WeightGoal,
    PreferenceGoal,
    ProjectRequirementGoal,
)
from benchmarking.evaluations.interfaces import Goal, Scenario


class ProjectRequirementPreferenceDiversifyGender(Scenario):
    def __init__(self, max_project_preferences: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_project_preferences = max_project_preferences

    @property
    def name(self) -> str:
        return "Meet Project Requirements, Project Preferences, and Diversify Gender"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(DiversifyType.DIVERSIFY, ScenarioAttribute.GENDER.value),
            ProjectRequirementGoal(),
            PreferenceGoal(
                direction=PreferenceDirection.INCLUDE,
                subject=PreferenceSubject.PROJECTS,
                max_project_preferences=self.max_project_preferences,
            ),
            WeightGoal(
                diversity_goal_weight=3,
                project_preference_weight=2,
                project_requirement_weight=1,
            ),
        ]
