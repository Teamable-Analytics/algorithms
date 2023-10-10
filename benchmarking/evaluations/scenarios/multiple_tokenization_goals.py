from typing import List

from api.models.enums import (
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
)
from api.models.tokenization_constraint import TokenizationConstraint
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class MultipleTokenizationGoals(Scenario):
    def __init__(self, value_of_gpa: int, value_of_race: int, value_of_age):
        self.value_of_gpa = value_of_gpa
        self.value_of_race = value_of_race
        self.value_of_age = value_of_age

    def name(self) -> str:
        return "Scenario to run multiple tokenization goals"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.GPA.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MAX_OF,
                    threshold=3,
                    value=self.value_of_gpa,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.RACE.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_race,
                ),
            ),
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.AGE.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MAX_OF,
                    threshold=3,
                    value=self.value_of_age,
                ),
            ),
            WeightGoal(diversity_goal_weight=1),
        ]
