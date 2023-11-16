from typing import Dict, List

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    RandomAlgorithmConfig,
    WeightAlgorithmConfig,
)
from api.ai.priority_algorithm.mutations import (
    mutate_local_max,
    mutate_random_swap,
    mutate_local_max_random,
    mutate_local_max_double_random,
    mutate_robinhood,
    mutate_robinhood_holistic,
)
from api.models.enums import ScenarioAttribute, Gender, AlgorithmType
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.average_gini_index import (
    AverageGiniIndex,
)
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


class DiversifyGenderMin2MaxTime(Run):
    @staticmethod
    def start(num_trials: int = 10, generate_graphs: bool = True):
        """
        Goal: Run diversify gender scenario while varying the maximum time argument for the priority algorithm.
        """

        # Defining our changing x-values (in the graph sense)
        times = list(range(2, 21, 2))
        ratio_of_female_students = 0.4
        max_iterate = 300
        number_of_students = 200
        number_of_teams = 40
        max_keep = 3
        max_spread = 3
        scenario = DiversifyGenderMin2Female(value_of_female=Gender.FEMALE.value)

        graph_runtime_dict = {}
        graph_avg_gini_dict = {}
        graph_priority_dict = {}
        graph_dicts = [
            graph_runtime_dict,
            graph_avg_gini_dict,
            graph_priority_dict,
        ]

        metrics: Dict[str, TeamSetMetric] = {
            "AverageGiniIndex": AverageGiniIndex(
                attribute=ScenarioAttribute.GENDER.value
            ),
            "MaxGiniIndex": MaximumGiniIndex(attribute=ScenarioAttribute.GENDER.value),
            "MinGiniIndex": MinimumGiniIndex(attribute=ScenarioAttribute.GENDER.value),
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
        }

        artifacts: Dict[int, SimulationSetArtifact] = {}

        for time in times:
            print("TIME /", time)
            # set up either mock or real data
            student_provider_settings = MockStudentProviderSettings(
                number_of_students=number_of_students,
                attribute_ranges={
                    ScenarioAttribute.GENDER.value: [
                        (Gender.MALE, 1 - ratio_of_female_students),
                        (Gender.FEMALE, ratio_of_female_students),
                    ],
                },
            )

            simulation_set_artifact = SimulationSet(
                settings=SimulationSettings(
                    num_teams=number_of_teams,
                    scenario=scenario,
                    student_provider=MockStudentProvider(student_provider_settings),
                    cache_key=f"diversify_gender_min_2_max_time_{time}_seconds",
                ),
                algorithm_set={
                    AlgorithmType.RANDOM: [RandomAlgorithmConfig()],
                    AlgorithmType.WEIGHT: [WeightAlgorithmConfig()],
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_ITERATE=max_iterate,
                            MAX_TIME=time,
                            MAX_KEEP=max_keep,
                            MAX_SPREAD=max_spread,
                        ),
                        PriorityAlgorithmConfig(
                            name="local_max",
                            MUTATIONS=[(mutate_local_max, 1), (mutate_random_swap, 2)],
                            MAX_TIME=time,
                            MAX_ITERATE=max_iterate,
                            MAX_KEEP=max_keep,
                            MAX_SPREAD=max_spread,
                        ),
                        PriorityAlgorithmConfig(
                            name="local_max_random",
                            MUTATIONS=[
                                (mutate_local_max_random, 1),
                                (mutate_random_swap, 2),
                            ],
                            MAX_TIME=time,
                            MAX_ITERATE=max_iterate,
                            MAX_KEEP=max_keep,
                            MAX_SPREAD=max_spread,
                        ),
                        PriorityAlgorithmConfig(
                            name="local_max_double_random",
                            MUTATIONS=[
                                (mutate_local_max_double_random, 1),
                                (mutate_random_swap, 2),
                            ],
                            MAX_TIME=time,
                            MAX_ITERATE=max_iterate,
                            MAX_KEEP=max_keep,
                            MAX_SPREAD=max_spread,
                        ),
                        PriorityAlgorithmConfig(
                            name="local_max_pure_double_random",
                            MUTATIONS=[(mutate_local_max_double_random, 3)],
                            MAX_TIME=time,
                            MAX_ITERATE=max_iterate,
                            MAX_KEEP=max_keep,
                            MAX_SPREAD=max_spread,
                        ),
                        PriorityAlgorithmConfig(
                            name="robinhood",
                            MUTATIONS=[(mutate_robinhood, 3)],
                            MAX_TIME=time,
                            MAX_ITERATE=max_iterate,
                            MAX_KEEP=max_keep,
                            MAX_SPREAD=max_spread,
                        ),
                        PriorityAlgorithmConfig(
                            name="robinhood_holistic",
                            MUTATIONS=[(mutate_robinhood_holistic, 3)],
                            MAX_TIME=time,
                            MAX_ITERATE=max_iterate,
                            MAX_KEEP=max_keep,
                            MAX_SPREAD=max_spread,
                        ),
                    ],
                },
            ).run(num_runs=num_trials)
            artifacts[time] = simulation_set_artifact

        if generate_graphs:
            for time, artifact in artifacts.items():
                insight_set: Dict[str, Dict[str, List[float]]] = Insight.get_output_set(
                    artifact=artifact, metrics=list(metrics.values())
                )

                average_ginis = Insight.average_metric(insight_set, "AverageGiniIndex")
                average_runtimes = Insight.average_metric(
                    insight_set, Insight.KEY_RUNTIMES
                )
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
                                x_data=[time],
                                y_data=[data],
                                name=name,
                            )
                        else:
                            graph_dicts[i][name].x_data.append(time)
                            graph_dicts[i][name].y_data.append(data)

            line_graph(
                LineGraphMetadata(
                    x_label="Time (seconds)",
                    y_label="Run time (seconds)",
                    title="Diversify Gender With Min of Two Runtimes",
                    data=list(graph_runtime_dict.values()),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Time (seconds)",
                    y_label="Average Gini Index",
                    title="Diversify Gender With Min of Two Average Gini Index",
                    data=list(graph_avg_gini_dict.values()),
                    y_lim=GraphAxisRange(
                        *metrics["AverageGiniIndex"].theoretical_range
                    ),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Time (seconds)",
                    y_label="Priorities Satisfied",
                    title="Diversity Gender With Min of Two Satisfied Priorities",
                    data=list(graph_priority_dict.values()),
                    y_lim=GraphAxisRange(
                        *metrics["PrioritySatisfaction"].theoretical_range
                    ),
                )
            )


if __name__ == "__main__":
    typer.run(DiversifyGenderMin2MaxTime.start)
