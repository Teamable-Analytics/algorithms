from typing import List

from restructure.models.enums import DiversifyType, ScenarioAttribute
from restructure.simulations.evaluations.interfaces import Scenario, Goal
from restructure.simulations.evaluations.scenarios.goals import (
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
