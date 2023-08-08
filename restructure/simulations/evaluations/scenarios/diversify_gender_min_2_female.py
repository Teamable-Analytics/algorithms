from typing import List

from restructure.models.enums import (
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
)
from restructure.simulations.evaluations.interfaces import (
    Scenario,
    TokenizationConstraint, Goal,
)
from restructure.simulations.evaluations.goals import DiversityGoal


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
        ]
