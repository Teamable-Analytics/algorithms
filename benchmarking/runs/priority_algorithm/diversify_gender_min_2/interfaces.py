from functools import cached_property
from typing import Dict

from api.models.enums import ScenarioAttribute, Gender
from benchmarking.evaluations.interfaces import Scenario, TeamSetMetric
from benchmarking.evaluations.metrics.average_gini_index import AverageGiniIndex
from benchmarking.evaluations.metrics.maximum_gini_index import MaximumGiniIndex
from benchmarking.evaluations.metrics.minimum_gini_index import MinimumGiniIndex
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.diversify_gender_min_2_female import (
    DiversifyGenderMin2Female,
)
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.goal_to_priority import goals_to_priorities


class PriorityAlgorithmParameters(Run):
    MAX_KEEP = 3
    MAX_SPREAD = 3
    MAX_ITERATE = 300
    MAX_TIME = 20
    RATIO_OF_FEMALE_STUDENT = 0.4
    NUMBER_OF_STUDENTS = 200
    NUMBER_OF_TEAMS = 40

    @property
    def metrics(self) -> Dict[str, TeamSetMetric]:
        return {
            "AverageGiniIndex": AverageGiniIndex(
                attribute=ScenarioAttribute.GENDER.value
            ),
            "MaxGiniIndex": MaximumGiniIndex(attribute=ScenarioAttribute.GENDER.value),
            "MinGiniIndex": MinimumGiniIndex(attribute=ScenarioAttribute.GENDER.value),
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(self.scenario.goals),
                False,
            ),
        }

    @cached_property
    def scenario(self) -> Scenario:
        return DiversifyGenderMin2Female(value_of_female=Gender.FEMALE.value)
