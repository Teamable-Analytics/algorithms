from typing import List

from api.models.enums import (
    DiversifyType,
    ScenarioAttribute,
    Gender,
    TokenizationConstraintDirection,
    Race,
    YearLevel,
)
from api.models.tokenization_constraint import TokenizationConstraint
from benchmarking.evaluations.goals import WeightGoal, DiversityGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class ConcentrateTimeSlotDiversifyGenderMin2AndDiversifyYearLevel(Scenario):
    def __init__(
        self,
        max_num_choices: int,
        value_of_female: int = Gender.FEMALE,
    ):
        super().__init__()
        self.value_of_female = value_of_female
        self.max_num_choices = max_num_choices

    @property
    def name(self):
        return "Concentrate on Timeslot, Diversify Female Min of Two, and Diversify Year Level"

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
                ScenarioAttribute.YEAR_LEVEL.value,
            ),
            WeightGoal(diversity_goal_weight=1),
        ]


class DiversifyGenderMin2ConcentrateTimeSlotAndDiversifyYearLevel(Scenario):
    def __init__(
        self,
        max_num_choices: int,
        value_of_female: int = Gender.FEMALE,
    ):
        super().__init__()
        self.value_of_female = value_of_female
        self.max_num_choices = max_num_choices

    @property
    def name(self):
        return "Concentrate on Timeslot, Diversify Female Min of Two, and Diversify Year Level"

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
