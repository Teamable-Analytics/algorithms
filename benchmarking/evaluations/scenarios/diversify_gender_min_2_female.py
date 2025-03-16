from typing import List

from algorithms.dataclasses.enums import (
    DiversifyType,
    TokenizationConstraintDirection,
)
from benchmarking.evaluations.enums import (
    ScenarioAttribute,
)
from benchmarking.evaluations.interfaces import (
    Scenario,
    Goal,
)
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from algorithms.dataclasses.tokenization_constraint import TokenizationConstraint


class DiversifyGenderMin2Female(Scenario):
    def __init__(self, value_of_female: int):
        self.value_of_female = value_of_female

    @property
    def name(self):
        return "Diversify on gender with a minimum of 2 female"

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
            WeightGoal(diversity_goal_weight=1),
        ]
