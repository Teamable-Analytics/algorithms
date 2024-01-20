from typing import List

from api.models.enums import DiversifyType, ScenarioAttribute, Gender, TokenizationConstraintDirection
from api.models.tokenization_constraint import TokenizationConstraint
from benchmarking.evaluations.goals import WeightGoal, DiversityGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class ConcentrateTimeslotAndDiversifyGenderMin2Female(Scenario):
    def __init__(self, value_of_female: int = Gender.FEMALE):
        super().__init__()
        self.value_of_female = value_of_female

    @property
    def name(self):
        return "Concentrate on Timeslot and Diversify Female min of 2"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(DiversifyType.CONCENTRATE, ScenarioAttribute.TIMESLOT_AVAILABILITY.value),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GENDER.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_female,
                )
            ),
            WeightGoal(diversity_goal_weight=1),
        ]
