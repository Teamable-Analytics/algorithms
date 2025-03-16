from typing import List

from algorithms.dataclasses.enums import DiversifyType
from benchmarking.evaluations.goals import DiversityGoal
from benchmarking.evaluations.interfaces import TeamSetMetric, Scenario


class TestMetric(TeamSetMetric):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calculate(self, team_set: "TeamSet") -> float:
        return 1


class TestScenario(Scenario):
    @property
    def name(self) -> str:
        return "Test Scenario"

    @property
    def goals(self) -> List["Goal"]:
        return [
            DiversityGoal(
                strategy=DiversifyType.DIVERSIFY,
                attribute=1,
            )
        ]
