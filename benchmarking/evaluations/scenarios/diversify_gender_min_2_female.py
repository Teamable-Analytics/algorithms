from typing import List, Callable

from api.models.enums import (
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
)
from api.models.student import Student
from api.models.team import TeamShell
from benchmarking.evaluations.interfaces import (
    Scenario,
    Goal,
)
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal, UtilityGoal
from api.models.tokenization_constraint import TokenizationConstraint


class DiversifyGenderMin2Female(Scenario):
    def __init__(self, value_of_female: int, utility_function: Callable[[Student, TeamShell], float]):
        self.value_of_female = value_of_female
        self.utility_function = utility_function

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
            UtilityGoal(utility_function=self.utility_function),
        ]
