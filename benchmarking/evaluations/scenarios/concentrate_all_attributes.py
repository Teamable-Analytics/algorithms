from typing import List

from models.enums import DiversifyType, ScenarioAttribute
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.goals import (
    DiversityGoal,
    WeightGoal,
)


class ConcentrateAllAttributes(Scenario):
    @property
    def name(self):
        return (
            "Concentrate on all attributes (age, gender, gpa, race, major, year level)"
        )

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(DiversifyType.CONCENTRATE, ScenarioAttribute.AGE.value),
            DiversityGoal(DiversifyType.CONCENTRATE, ScenarioAttribute.GENDER.value),
            DiversityGoal(DiversifyType.CONCENTRATE, ScenarioAttribute.GPA.value),
            DiversityGoal(DiversifyType.CONCENTRATE, ScenarioAttribute.RACE.value),
            DiversityGoal(DiversifyType.CONCENTRATE, ScenarioAttribute.MAJOR.value),
            DiversityGoal(
                DiversifyType.CONCENTRATE, ScenarioAttribute.YEAR_LEVEL.value
            ),
            WeightGoal(diversity_goal_weight=1),
        ]
