from typing import List

from api.models.enums import (
    DiversifyType,
    ScenarioAttribute,
)
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class ConcentrateTimeslotConcentrateGenderDiversifyYearLevel(Scenario):
    # This scenario concentrates timeslot, concentrates gender, and diversifies year level.
    def __init__(
        self,
        max_num_choices: int,
    ):
        super().__init__()
        self.max_num_choices = max_num_choices

    @property
    def name(self):
        return (
            "Concentrate on Timeslot, Concentrate All Genders, and Diversify Year Level"
        )

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
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.YEAR_LEVEL.value,
                max_num_choices=1,
            ),
            WeightGoal(diversity_goal_weight=1),
        ]


class ConcentrateGenderConcentrateTimeslotDiversifyYearLevel(Scenario):
    # This scenario concentrates gender, concentrates timeslot, and diversifies year level.
    # It is the same as the above with a slightly different ordering.
    def __init__(
        self,
        max_num_choices: int,
    ):
        super().__init__()
        self.max_num_choices = max_num_choices

    @property
    def name(self):
        return (
            "Concentrate All Gender, Concentrate on Timeslot, and Diversify Year Level"
        )

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.GENDER.value,
                max_num_choices=1,
            ),
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.TIMESLOT_AVAILABILITY.value,
                max_num_choices=self.max_num_choices,
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.YEAR_LEVEL.value,
                max_num_choices=1,
            ),
            WeightGoal(diversity_goal_weight=1),
        ]
