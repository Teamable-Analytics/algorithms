from typing import List

from api.models.enums import (
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
)
from api.models.tokenization_constraint import TokenizationConstraint
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class CustomScenario(Scenario):
    def __init__(self, value_of_female: int, value_of_gpa: int, value_of_age: int):
        self.value_of_female = value_of_female
        self.value_of_gpa = value_of_gpa
        self.value_of_age = value_of_age

    def name(self) -> str:
        return "Scenario to run three tokenization constraints with diversify gender min 2, concentrate GPA max 5, and concentrate age max 5."

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
                ScenarioAttribute.GPA.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MAX_OF,
                    threshold=5,
                    value=self.value_of_gpa,
                ),
            ),
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.AGE.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MAX_OF,
                    threshold=5,
                    value=self.value_of_age,
                ),
            ),
            WeightGoal(diversity_goal_weight=1),
        ]
