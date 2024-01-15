from typing import List

from api.models.enums import (
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
)
from benchmarking.evaluations.interfaces import (
    Scenario,
    Goal,
)
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from api.models.tokenization_constraint import TokenizationConstraint


class ConcentrateTimeAvailabilityDiversifyGenderMin2Female(Scenario):
    def __init__(self, value_of_female: int):
        self.value_of_female = value_of_female

    @property
    def name(self):
        return "Concentrate time availability and Diversify on gender with a minimum of 2 female"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.TIMESLOT_AVAILABILITY.value,
            ),
            # DiversityGoal(
            #     DiversifyType.DIVERSIFY,
            #     ScenarioAttribute.GENDER.value,
            #     tokenization_constraint=TokenizationConstraint(
            #         direction=TokenizationConstraintDirection.MIN_OF,
            #         threshold=2,
            #         value=self.value_of_female,
            #     ),
            # ),
            WeightGoal(diversity_goal_weight=1),
        ]
