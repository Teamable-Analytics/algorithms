from typing import List

from models.enums import DiversifyType, ScenarioAttribute
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.goals import (
    DiversityGoal,
    WeightGoal,
)


class ScenarioDiversifyGenderOnly(Scenario):
    @property
    def name(self):
        return "Diversify on gender"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(DiversifyType.DIVERSIFY, ScenarioAttribute.GENDER.value),
            WeightGoal(diversity_goal_weight=1),
        ]
