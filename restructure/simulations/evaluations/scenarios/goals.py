from dataclasses import dataclass

from restructure.models.enums import DiversifyType, ScenarioAttribute
from restructure.simulations.evaluations.enums import (
    PreferenceDirection,
    PreferenceSubject,
)
from restructure.simulations.evaluations.interfaces import Goal, TokenizationConstraint


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


@dataclass
class WeightGoal(Goal):
    project_requirement_weight: int
    social_preference_weight: int
    diversity_goal_weight: int
    project_preference_weight: int
