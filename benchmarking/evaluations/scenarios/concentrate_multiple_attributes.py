from typing import List

from models.enums import DiversifyType, ScenarioAttribute
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.goals import (
    DiversityGoal,
    WeightGoal,
)


class ConcentrateMultipleAttributes(Scenario):

    def __init__(self, attributes: List[ScenarioAttribute]):
        self.attributes = attributes

    @property
    def name(self):
        attribute_name_list = ", ".join([_.name for _ in self.attributes])
        return (
            f"Concentrate on multiple attributes ({attribute_name_list})"
        )

    @property
    def goals(self) -> List[Goal]:
        return [
            *[
                DiversityGoal(DiversifyType.CONCENTRATE, attribute.value)
                for attribute in self.attributes
            ],
            WeightGoal(diversity_goal_weight=1),
        ]
