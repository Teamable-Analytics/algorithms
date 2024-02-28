from typing import List

from api.models.enums import (
    Gender,
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
)
from api.models.tokenization_constraint import TokenizationConstraint
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class ConcentrateTimeSlotDiversifyAllGenderMin2DiversifyYearLevel(Scenario):
    # This scenario diversifies all genders with min 2 to better compare with group matcher, which guarantees no individual will have solo status
    def __init__(
        self,
        max_num_choices: int,
        value_of_male: int = Gender.MALE,
        value_of_female: int = Gender.FEMALE,
        value_of_non_binary: int = Gender.NON_BINARY,
        value_of_non_answer: int = Gender.NA,
    ):
        super().__init__()
        self.value_of_female = value_of_female
        self.max_num_choices = max_num_choices
        self.value_of_male = value_of_male
        self.value_of_non_binary = value_of_non_binary
        self.value_of_non_answer = value_of_non_answer

    @property
    def name(self):
        return "Concentrate on Timeslot, Diversify All Genders Min of Two, and Diversify Year Level"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.TIMESLOT_AVAILABILITY.value,
                max_num_choices=self.max_num_choices,
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GENDER.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_female,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GENDER.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_non_binary,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GENDER.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_male,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GENDER.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_non_answer,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.YEAR_LEVEL.value,
            ),
            WeightGoal(diversity_goal_weight=1),
        ]


class ConcentrateTimeSlotDiversifyAllGenderMin2DiversifyYearLevelSwitchedOrdering(Scenario):
    # This scenario diversifies all genders with min 2 to better compare with group matcher, which guarantees no individual will have solo status
    def __init__(
        self,
        max_num_choices: int,
        value_of_male: int = Gender.MALE,
        value_of_female: int = Gender.FEMALE,
        value_of_non_binary: int = Gender.NON_BINARY,
        value_of_non_answer: int = Gender.NA,
    ):
        super().__init__()
        self.value_of_female = value_of_female
        self.max_num_choices = max_num_choices
        self.value_of_male = value_of_male
        self.value_of_non_binary = value_of_non_binary
        self.value_of_non_answer = value_of_non_answer

    @property
    def name(self):
        return "Concentrate on Timeslot, Diversify All Genders Min of Two, and Diversify Year Level"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GENDER.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_female,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GENDER.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_non_binary,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GENDER.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_male,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GENDER.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_non_answer,
                ),
            ),
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.TIMESLOT_AVAILABILITY.value,
                max_num_choices=self.max_num_choices,
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.YEAR_LEVEL.value,
            ),
            WeightGoal(diversity_goal_weight=1),
        ]
