from typing import List

from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal
from api.dataclasses.enums import DiversifyType
from benchmarking.evaluations.enums import ScenarioAttribute


class ConcentrateGPA(Scenario):
    @property
    def name(self):
        return "Concentrate on GPA"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(DiversifyType.CONCENTRATE, ScenarioAttribute.GPA.value),
            WeightGoal(diversity_goal_weight=1),
        ]
