from typing import List

from api.dataclasses.enums import (
    DiversifyType,
    ScenarioAttribute,
    Gender,
    TokenizationConstraintDirection,
    Race,
)
from api.dataclasses.tokenization_constraint import TokenizationConstraint
from benchmarking.evaluations.goals import WeightGoal, DiversityGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class ConcentrateTimeslotAndDiversifyGenderMin2Female(Scenario):
    def __init__(
        self,
        max_num_choices: int,
        value_of_female: int = Gender.FEMALE.value,
        value_of_african: int = Race.African.value,
    ):
        super().__init__()
        self.value_of_female = value_of_female
        self.value_of_african = value_of_african
        self.max_num_choices = max_num_choices

    @property
    def name(self):
        return "Concentrate on Timeslot and Diversify Female min of 2"

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
            WeightGoal(diversity_goal_weight=1),
        ]
