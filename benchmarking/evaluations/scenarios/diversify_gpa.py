from typing import List

from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal
from api.dataclasses.enums import DiversifyType, ScenarioAttribute


class DiversifyGPA(Scenario):
    @property
    def name(self):
        return "Diversify on GPA"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(DiversifyType.CONCENTRATE, ScenarioAttribute.GPA.value),
            WeightGoal(diversity_goal_weight=1),
        ]
