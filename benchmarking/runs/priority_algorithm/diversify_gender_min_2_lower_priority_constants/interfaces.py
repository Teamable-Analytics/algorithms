from functools import cached_property
from typing import Dict, List

from api.ai.interfaces.algorithm_config import (
    RandomAlgorithmConfig,
    WeightAlgorithmConfig,
    PriorityAlgorithmConfig,
)
from api.ai.priority_algorithm.mutations.local_max import LocalMaxMutation
from api.ai.priority_algorithm.mutations.local_max_double_random import (
    LocalMaxDoubleRandomMutation,
)
from api.ai.priority_algorithm.mutations.local_max_random import LocalMaxRandomMutation
from api.ai.priority_algorithm.mutations.mutation_set import MutationSet
from api.ai.priority_algorithm.mutations.random_swap import RandomSwapMutation
from api.ai.priority_algorithm.mutations.robinhood import RobinhoodMutation
from api.ai.priority_algorithm.mutations.robinhood_holistic import (
    RobinhoodHolisticMutation,
)
from api.dataclasses.enums import ScenarioAttribute, Gender, AlgorithmType
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProviderSettings,
    MockStudentProvider,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
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
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings


class DiversifyGenderMin2LowerPriorityConstants(Run):
    MAX_KEEP = 1
    MAX_SPREAD = 1
    MAX_ITERATE = 5
    MAX_TIME = 2
    RATIO_OF_FEMALE_STUDENT = 0.4
    NUMBER_OF_STUDENTS = 250
    NUMBER_OF_TEAMS = 50

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

    def mock_student_provider_settings(self, **kwargs):
        return MockStudentProviderSettings(
            number_of_students=kwargs.get(
                "number_of_students", self.NUMBER_OF_STUDENTS
            ),
            attribute_ranges={
                ScenarioAttribute.GENDER.value: [
                    (Gender.MALE, 1 - self.RATIO_OF_FEMALE_STUDENT),
                    (Gender.FEMALE, self.RATIO_OF_FEMALE_STUDENT),
                ],
            },
        )

    def simulation_set(self, cache_key: str, **kwargs):
        max_iterate = kwargs.get("max_iterate", self.MAX_ITERATE)
        max_spread = kwargs.get("max_spread", self.MAX_SPREAD)
        max_time = kwargs.get("max_time", self.MAX_TIME)
        max_keep = kwargs.get("max_keep", self.MAX_KEEP)
        num_teams = kwargs.get("number_of_teams", self.NUMBER_OF_TEAMS)
        print(f"Max iterate: {max_iterate}, max spread: {max_spread}")
        return SimulationSet(
            settings=SimulationSettings(
                num_teams=num_teams,
                scenario=self.scenario,
                student_provider=MockStudentProvider(
                    self.mock_student_provider_settings(**kwargs)
                ),
                cache_key=cache_key,
            ),
            algorithm_set={
                AlgorithmType.RANDOM: [RandomAlgorithmConfig()],
                AlgorithmType.WEIGHT: [WeightAlgorithmConfig()],
                AlgorithmType.PRIORITY: [
                    PriorityAlgorithmConfig(
                        MAX_ITERATE=max_iterate,
                        MAX_TIME=max_time,
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=max_spread,
                    ),
                    PriorityAlgorithmConfig(
                        name="local_max",
                        MUTATIONS=MutationSet(
                            [
                                (LocalMaxMutation(), 1),
                                (RandomSwapMutation(), max_spread - 1),
                            ]
                        ),
                        MAX_TIME=max_time,
                        MAX_ITERATE=max_iterate,
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=max_spread,
                    ),
                    PriorityAlgorithmConfig(
                        name="local_max_random",
                        MUTATIONS=MutationSet(
                            [
                                (LocalMaxRandomMutation(), 1),
                                (RandomSwapMutation(), max_spread - 1),
                            ]
                        ),
                        MAX_TIME=max_time,
                        MAX_ITERATE=max_iterate,
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=max_spread,
                    ),
                    PriorityAlgorithmConfig(
                        name="local_max_double_random",
                        MUTATIONS=MutationSet(
                            [
                                (LocalMaxDoubleRandomMutation(), 1),
                                (RandomSwapMutation(), max_spread - 1),
                            ]
                        ),
                        MAX_TIME=max_time,
                        MAX_ITERATE=max_iterate,
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=max_spread,
                    ),
                    PriorityAlgorithmConfig(
                        name="local_max_pure_double_random",
                        MUTATIONS=MutationSet(
                            [(LocalMaxDoubleRandomMutation(), max_spread)]
                        ),
                        MAX_TIME=max_time,
                        MAX_ITERATE=max_iterate,
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=max_spread,
                    ),
                    PriorityAlgorithmConfig(
                        name="robinhood",
                        MUTATIONS=MutationSet([(RobinhoodMutation(), max_spread)]),
                        MAX_TIME=max_time,
                        MAX_ITERATE=max_iterate,
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=max_spread,
                    ),
                    PriorityAlgorithmConfig(
                        name="robinhood_holistic",
                        MUTATIONS=MutationSet(
                            [(RobinhoodHolisticMutation(), max_spread)]
                        ),
                        MAX_TIME=max_time,
                        MAX_ITERATE=max_iterate,
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=max_spread,
                    ),
                ],
            },
        )

    @cached_property
    def scenario(self) -> Scenario:
        return DiversifyGenderMin2Female(value_of_female=Gender.FEMALE.value)

    def generate_graphs(
        self,
        artifacts: Dict[int, SimulationSetArtifact],
        graph_names: Dict[str, str],
        x_label: str,
    ):
        graph_runtime_dict = {}
        graph_avg_gini_dict = {}
        graph_priority_dict = {}
        graph_dicts = [
            graph_runtime_dict,
            graph_avg_gini_dict,
            graph_priority_dict,
        ]

        for item, artifact in artifacts.items():
            insight_set: Dict[str, Dict[str, List[float]]] = Insight.get_output_set(
                artifact=artifact, metrics=list(self.metrics.values())
            )

            average_ginis = Insight.average_metric(insight_set, "AverageGiniIndex")
            average_runtimes = Insight.average_metric(insight_set, Insight.KEY_RUNTIMES)
            satisfied_priorities = Insight.average_metric(
                insight_set, "PrioritySatisfaction"
            )

            metric_values = [
                average_runtimes,
                average_ginis,
                satisfied_priorities,
            ]

            # Data processing for graph
            for i, metric in enumerate(metric_values):
                for name, data in metric.items():
                    if name not in graph_dicts[i]:
                        graph_dicts[i][name] = GraphData(
                            x_data=[item],
                            y_data=[data],
                            name=name,
                        )
                    else:
                        graph_dicts[i][name].x_data.append(item)
                        graph_dicts[i][name].y_data.append(data)

        line_graph(
            LineGraphMetadata(
                x_label=x_label,
                y_label="Run time (seconds)",
                title=graph_names.get(Insight.KEY_RUNTIMES),
                data=list(graph_runtime_dict.values()),
            )
        )

        line_graph(
            LineGraphMetadata(
                x_label=x_label,
                y_label="Average Gini Index",
                title=graph_names.get("AverageGiniIndex"),
                data=list(graph_avg_gini_dict.values()),
                y_lim=GraphAxisRange(
                    *self.metrics["AverageGiniIndex"].theoretical_range
                ),
            )
        )

        line_graph(
            LineGraphMetadata(
                x_label=x_label,
                y_label="Priorities Satisfied",
                title=graph_names.get("PrioritySatisfaction"),
                data=list(graph_priority_dict.values()),
                y_lim=GraphAxisRange(
                    *self.metrics["PrioritySatisfaction"].theoretical_range
                ),
            )
        )
