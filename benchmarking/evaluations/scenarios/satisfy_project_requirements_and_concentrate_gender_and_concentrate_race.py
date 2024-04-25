from typing import List

from api.dataclasses.enums import DiversifyType, ScenarioAttribute
from benchmarking.evaluations.goals import ProjectRequirementGoal, DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class SatisfyProjectRequirementsAndConcentrateGenderAndConcentrateRace(Scenario):
    @property
    def name(self) -> str:
        return "Satisfy Project Requirements and Concentrate Gender and Concentrate Race"

    @property
    def goals(self) -> List[Goal]:
        return [
            ProjectRequirementGoal(),
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.GENDER.value,
                max_num_choices=1,
            ),
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.RACE.value,
                max_num_choices=1,
            ),
            WeightGoal(project_requirement_weight=2, diversity_goal_weight=1)
        ]
