from typing import List

from api.models.enums import Gender
from benchmarking.evaluations.interfaces import Scenario, Goal


class COSC341Scenario(Scenario):
    def __init__(
        self,
        max_num_choices: int,
        value_of_female: int = Gender.FEMALE,
    ):
        super().__init__()
        self.value_of_female = value_of_female
        self.max_num_choices = max_num_choices

    @property
    def name(self) -> str:
        return "COSC 341 Scenario"

    @property
    def goals(self) -> List[Goal]:
        return []
