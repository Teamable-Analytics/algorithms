from typing import List

from models.enums import (
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
)
from benchmarking.evaluations.interfaces import (
    Scenario,
    TokenizationConstraint,
    Goal,
)
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal


class DiversifySocialMin2Friends(Scenario):
    def __init__(self, value_of_friend: int):
        self.value_of_friend = value_of_friend

    @property
    def name(self):
        return "Diversify on social with a minimum of 2 friends"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.SOCIAL.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_friend,
                ),
            ),
            WeightGoal(diversity_goal_weight=1),
        ]
