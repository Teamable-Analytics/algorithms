from typing import List

from restructure.models.enums import DiversifyType, ScenarioAttribute
from restructure.simulations.evaluations.interfaces import Scenario, Goal
from restructure.simulations.evaluations.scenarios.goals import DiversityGoal


class ScenarioDiversifyGender(Scenario):
    @property
    def name(self):
        return "Diversify on Gender"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(DiversifyType.DIVERSIFY, ScenarioAttribute.GENDER.value),
        ]
