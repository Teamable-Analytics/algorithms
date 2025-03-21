from typing import List

from algorithms.dataclasses.enums import (
    DiversifyType,
)
from benchmarking.evaluations.enums import (
    ScenarioAttribute,
    Gender,
    Race,
)
from benchmarking.evaluations.goals import WeightGoal, DiversityGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class ConcentrateTimeslotsAndConcentrateGenderAndConcentrateRace(Scenario):
    def __init__(
        self,
        max_num_choices: int,
        value_of_female: int = Gender.FEMALE.value,
        value_of_african: int = Race.African.value,
    ):
        super().__init__()
        self.value_of_female = value_of_female
        self.value_of_african = value_of_african
        self.max_num_choices = max_num_choices

    @property
    def name(self):
        return "Concentrate on Timeslots and Concentrate Gender and Concentrate Race"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.TIMESLOT_AVAILABILITY.value,
                max_num_choices=self.max_num_choices,
            ),
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
            WeightGoal(diversity_goal_weight=1),
        ]
