from typing import List

from api.models.enums import (
    DiversifyType,
    ScenarioAttribute,
)
from benchmarking.evaluations.goals import DiversityGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class ConcentrateCampusLocation(Scenario):
    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return "Concentrate on Campus Location"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.LOCATION.value,
                max_num_choices=1,
            ),
        ]
