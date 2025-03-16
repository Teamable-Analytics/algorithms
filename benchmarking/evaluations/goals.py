from dataclasses import dataclass
from typing import Optional

from benchmarking.evaluations.interfaces import Goal
from api.dataclasses.enums import DiversifyType, PreferenceDirection, PreferenceSubject
from api.dataclasses.tokenization_constraint import TokenizationConstraint


@dataclass
class DiversityGoal(Goal):
    strategy: DiversifyType
    attribute: int
    # the max number of values a student can have for the attribute_id, defaults to 1 when needed but not specified
    max_num_choices: Optional[int] = None
    importance: int = 999
    tokenization_constraint: TokenizationConstraint = None

    def __post_init__(self):
        if (
            self.strategy == DiversifyType.CONCENTRATE
            and not self.tokenization_constraint
        ):
            self.max_num_choices = (
                self.max_num_choices or 1
            )  # setting the default when needed, OR used because value cannot be 0
        # calls the super method after so that the validate method is processed after this default is set
        super().__post_init__()

    def validate(self):
        if self.max_num_choices and self.tokenization_constraint:
            print(
                "[Warning]: max_num_choices is not needed when using diversity goals with tokenization constraints."
            )
        if (
            self.strategy == DiversifyType.CONCENTRATE
            and not self.tokenization_constraint
            and not self.max_num_choices
        ):
            raise ValueError(
                "max_num_choices must be specified with strategy == CONCENTRATE and cannot be 0."
            )


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
    pass


@dataclass
class WeightGoal(Goal):
    project_requirement_weight: int = 0
    social_preference_weight: int = 0
    diversity_goal_weight: int = 0
    project_preference_weight: int = 0
