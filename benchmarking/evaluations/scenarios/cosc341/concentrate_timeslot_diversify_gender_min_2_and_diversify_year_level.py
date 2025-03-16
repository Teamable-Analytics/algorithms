from typing import List

from algorithms.dataclasses.enums import (
    DiversifyType,
    TokenizationConstraintDirection,
)
from benchmarking.evaluations.enums import (
    ScenarioAttribute,
    Gender,
)
from algorithms.dataclasses.tokenization_constraint import TokenizationConstraint
from benchmarking.evaluations.goals import WeightGoal, DiversityGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class ConcentrateTimeSlotDiversifyGenderMin2AndDiversifyYearLevel(Scenario):
    # This Scenario concentrates on timeslot, diversifies female gender with min 2, and diversifies year level.
    def __init__(
        self,
        value_of_female: int = Gender.FEMALE.value,
    ):
        super().__init__()
        self.value_of_female = value_of_female

    @property
    def name(self):
        return "Concentrate on Timeslot, Diversify Female Min of Two, and Diversify Year Level"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.TIMESLOT_AVAILABILITY.value,
                max_num_choices=6,
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
        value_of_female: int = Gender.FEMALE.value,
    ):
        super().__init__()
        self.value_of_female = value_of_female

    @property
    def name(self):
        return "Diversify Female Min of Two, Concentrate Timeslot, and Diversify Year Level"

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
                max_num_choices=6,
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.YEAR_LEVEL.value,
            ),
            WeightGoal(diversity_goal_weight=1),
        ]
