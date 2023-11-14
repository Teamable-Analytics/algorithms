from dataclasses import dataclass
from typing import Optional

from benchmarking.evaluations.enums import (
    PreferenceDirection,
    PreferenceSubject,
)
from benchmarking.evaluations.interfaces import Goal
from api.models.enums import DiversifyType, RequirementsCriteria
from api.models.tokenization_constraint import TokenizationConstraint


@dataclass
class DiversityGoal(Goal):
    strategy: DiversifyType
    attribute: int
    importance: int = 999
    tokenization_constraint: TokenizationConstraint = None


@dataclass
class PreferenceGoal(Goal):
    direction: PreferenceDirection
    subject: PreferenceSubject


@dataclass
class ProjectRequirementGoal(Goal):
    match_skills: bool
    criteria: Optional[
        RequirementsCriteria
    ] = RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED

    def validate(self):
        if not self.match_skills and self.criteria:
            raise ValueError(
                "If skills are not being matched at all, no matching criteria can be set!"
            )


@dataclass
class WeightGoal(Goal):
    project_requirement_weight: int = 0
    social_preference_weight: int = 0
    diversity_goal_weight: int = 0
    project_preference_weight: int = 0
