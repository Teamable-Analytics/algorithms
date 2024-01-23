from typing import List

from api.models.enums import (
    DiversifyType,
    ScenarioAttribute,
    Gender,
    TokenizationConstraintDirection,
    Race,
)
from api.models.tokenization_constraint import TokenizationConstraint
from benchmarking.evaluations.goals import WeightGoal, DiversityGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class ConcentrateTimeslotAndDiversifyGenderMin2Female(Scenario):
    def __init__(
        self, value_of_female: int = Gender.FEMALE, value_of_african: int = Race.African
    ):
        super().__init__()
        self.value_of_female = value_of_female
        self.value_of_african = value_of_african

    @property
    def name(self):
        return "Concentrate on Timeslot and Diversify Female min of 2"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.CONCENTRATE, ScenarioAttribute.TIMESLOT_AVAILABILITY.value
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
                ScenarioAttribute.RACE.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_african,
                ),
            ),
            WeightGoal(diversity_goal_weight=1),
        ]
