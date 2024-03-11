from typing import List

from api.dataclasses.enums import DiversifyType, ScenarioAttribute
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.goals import (
    DiversityGoal,
    WeightGoal,
)


class DiversifyGenderOnly(Scenario):
    @property
    def name(self):
        return "Diversify on gender"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(DiversifyType.DIVERSIFY, ScenarioAttribute.GENDER.value),
            WeightGoal(diversity_goal_weight=1),
        ]
