from functools import cached_property
from typing import Dict, List

from api.models.enums import ScenarioAttribute, Gender
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProviderSettings,
)
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
from benchmarking.simulation.simulation_set import SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class PriorityAlgorithmParameters(Run):
    MAX_KEEP = 3
    MAX_SPREAD = 3
    MAX_ITERATE = 300
    MAX_TIME = 20
    RATIO_OF_FEMALE_STUDENT = 0.4
    NUMBER_OF_STUDENTS = 200
    NUMBER_OF_TEAMS = 40

    @property
    def graph_dicts(self) -> List[Dict]:
        graph_runtime_dict = {}
        graph_avg_gini_dict = {}
        graph_priority_dict = {}
        return [
            graph_runtime_dict,
            graph_avg_gini_dict,
            graph_priority_dict,
        ]

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

    @property
    def mock_student_provider_settings(self, **kwargs):
        return MockStudentProviderSettings(
            number_of_students=kwargs["number_of_students"],
            attribute_ranges={
                ScenarioAttribute.GENDER.value: [
                    (Gender.MALE, 1 - kwargs["ratio_female_students"]),
                    (Gender.FEMALE, kwargs["ratio_female_students"]),
                ],
            },
        )

    @property
    def simulation_settings(self, **kwargs):
        return

    @property
    def simulation_set(self, **kwargs):
        return SimulationSet(
            settings=SimulationSettings(
                num_teams=kwargs["number_of_teams"],
                scenario=self.scenario,
                student_provider=self.mock_student_provider_settings(**kwargs),
                cache_key=f"priority_algorithm/diversify_gender_min_2/max_spread/{spread}",
            ),
            algorithm_set={
                AlgorithmType.RANDOM: [RandomAlgorithmConfig()],
                AlgorithmType.WEIGHT: [WeightAlgorithmConfig()],
                AlgorithmType.PRIORITY: [
                    PriorityAlgorithmConfig(
                        MAX_ITERATE=max_iterate,
                        MAX_TIME=max_time,
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=spread,
                    ),
                    PriorityAlgorithmConfig(
                        name="local_max",
                        MUTATIONS=[
                            (mutate_local_max, 1),
                            (mutate_random_swap, spread - 1),
                        ],
                        MAX_TIME=max_time,
                        MAX_ITERATE=max_iterate,
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=spread,
                    ),
                    PriorityAlgorithmConfig(
                        name="local_max_random",
                        MUTATIONS=[
                            (mutate_local_max_random, 1),
                            (mutate_random_swap, spread - 1),
                        ],
                        MAX_TIME=max_time,
                        MAX_ITERATE=max_iterate,
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=spread,
                    ),
                    PriorityAlgorithmConfig(
                        name="local_max_double_random",
                        MUTATIONS=[
                            (mutate_local_max_double_random, 1),
                            (mutate_random_swap, spread - 1),
                        ],
                        MAX_TIME=max_time,
                        MAX_ITERATE=max_iterate,
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=spread,
                    ),
                    PriorityAlgorithmConfig(
                        name="local_max_pure_double_random",
                        MUTATIONS=[(mutate_local_max_double_random, spread)],
                        MAX_TIME=max_time,
                        MAX_ITERATE=max_iterate,
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=spread,
                    ),
                    PriorityAlgorithmConfig(
                        name="robinhood",
                        MUTATIONS=[(mutate_robinhood, spread)],
                        MAX_TIME=max_time,
                        MAX_ITERATE=max_iterate,
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=spread,
                    ),
                    PriorityAlgorithmConfig(
                        name="robinhood_holistic",
                        MUTATIONS=[(mutate_robinhood_holistic, spread)],
                        MAX_TIME=max_time,
                        MAX_ITERATE=max_iterate,
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=spread,
                    ),
                ],
            },
        )

    @cached_property
    def scenario(self) -> Scenario:
        return DiversifyGenderMin2Female(value_of_female=Gender.FEMALE.value)
