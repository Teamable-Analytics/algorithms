from typing import List

from algorithms.dataclasses.enums import (
    DiversifyType,
)
from benchmarking.evaluations.enums import (
    ScenarioAttribute,
)
from benchmarking.evaluations.goals import DiversityGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class ConcentrateTimeslots(Scenario):
    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return "Concentrate on Timeslot"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.TIMESLOT_AVAILABILITY.value,
                max_num_choices=8,
            ),
        ]
