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
    max_num_friends: int = None
    max_num_enemies: int = None
    max_project_preferences: Optional[int] = None

    def validate(self):
        if (
            self.subject == PreferenceSubject.PROJECTS
            and not self.max_project_preferences
        ):
            raise ValueError(
                "Using the projects preference subject requires the specification of "
                "max_project_preferences"
            )
        if self.subject in [
            PreferenceSubject.FRIENDS,
            PreferenceSubject.ENEMIES,
        ] and (self.max_num_friends is None or self.max_num_enemies is None):
            raise ValueError(
                "Using the friends or enemies preference subject requires the specification of "
                "max_num_friends and max_num_enemies"
            )


@dataclass
class ProjectRequirementGoal(Goal):
    criteria: Optional[
        RequirementsCriteria
    ] = RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED


@dataclass
class WeightGoal(Goal):
    project_requirement_weight: int = 0
    social_preference_weight: int = 0
    diversity_goal_weight: int = 0
    project_preference_weight: int = 0
