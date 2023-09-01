from typing import List

from models.enums import (
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
)
from benchmarking.evaluations.interfaces import (
    Scenario,
    TokenizationConstraint, Goal,
)
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal


class ScenarioDiversifyGenderMin2Female(Scenario):

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
