import math
from typing import Dict, List

import typer

from api.ai.interfaces.algorithm_config import (
    RandomAlgorithmConfig,
    SocialAlgorithmConfig,
    WeightAlgorithmConfig,
    PriorityAlgorithmConfig,
)
from api.ai.priority_algorithm.mutations import mutate_local_max, mutate_random_swap
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.average_gini_index import AverageGiniIndex
from benchmarking.evaluations.metrics.maximum_gini_index import MaximumGiniIndex
from benchmarking.evaluations.metrics.minimum_gini_index import MinimumGiniIndex
from benchmarking.evaluations.scenarios.concentrate_gpa import ConcentrateGPA
from api.models.enums import ScenarioAttribute, Gpa, AlgorithmType
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings


class ConcentrateGpaRun(Run):
    def start(self, num_trials: int = 100, generate_graphs: bool = False):
        """
        Goal: Run concentrate GPA scenario, and measure the average, maximum, and minimum gini scores for gpa
        """

        # Define changing values
        class_sizes = list(range(50, 100, 50))
        ratio_of_a_students = 0.25
        ratio_of_b_students = 0.50
        ratio_of_c_students = 0.25

        # Graph variables
        graph_runtime_dict = {}
        graph_avg_gini_dict = {}
        graph_min_gini_dict = {}
        graph_max_gini_dict = {}
        graph_dicts = [
            graph_runtime_dict,
            graph_avg_gini_dict,
            graph_min_gini_dict,
            graph_max_gini_dict,
        ]

        metrics: Dict[str, TeamSetMetric] = {
            "AverageGiniIndex": AverageGiniIndex(attribute=ScenarioAttribute.GPA.value),
            "MaxGiniIndex": MaximumGiniIndex(attribute=ScenarioAttribute.GPA.value),
            "MinGiniIndex": MinimumGiniIndex(attribute=ScenarioAttribute.GPA.value),
        }

        artifacts: Dict[int, SimulationSetArtifact] = {}

        for class_size in class_sizes:
            print("CLASS SIZE /", class_size)

            number_of_teams = math.ceil(class_size / 5)

            student_provider_settings = MockStudentProviderSettings(
                number_of_students=class_size,
                attribute_ranges={
                    ScenarioAttribute.GPA.value: [
                        (Gpa.A, ratio_of_a_students),
                        (Gpa.B, ratio_of_b_students),
                        (Gpa.C, ratio_of_c_students),
                    ]
                },
            )

            simulation_set_artifact = SimulationSet(
                settings=SimulationSettings(
                    num_teams=number_of_teams,
                    scenario=ConcentrateGPA(),
                    student_provider=MockStudentProvider(student_provider_settings),
                    cache_key=f"concentrate_gpa_{number_of_teams}",
                ),
                algorithm_set={
                    AlgorithmType.RANDOM: [RandomAlgorithmConfig()],
                },
            ).run(num_runs=num_trials)
            artifacts[class_size] = simulation_set_artifact

        if generate_graphs:
            for class_size, artifact in artifacts.items():
                insight_set: Dict[str, Dict[str, List[float]]] = Insight.get_output_set(
                    artifact=artifact, metrics=list(metrics.values())
                )

                average_ginis = Insight.average_metric(insight_set, "AverageGiniIndex")
                maximum_ginis = Insight.average_metric(insight_set, "MaximumGiniIndex")
                minimum_ginis = Insight.average_metric(insight_set, "MinimumGiniIndex")
                average_runtimes = Insight.average_metric(
                    insight_set, Insight.KEY_RUNTIMES
                )
                metric_values = [
                    average_runtimes,
                    average_ginis,
                    minimum_ginis,
                    maximum_ginis,
                ]
                # Data processing for graph
                for i, metric in enumerate(metric_values):
                    for name, data in metric.items():
                        if name not in graph_dicts[i]:
                            graph_dicts[i][name] = GraphData(
                                x_data=[class_size],
                                y_data=[data],
                                name=name,
                            )
                        else:
                            graph_dicts[i][name].x_data.append(class_size)
                            graph_dicts[i][name].y_data.append(data)

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Run time (seconds)",
                    title="Concentrate GPA Runtimes",
                    data=list(graph_runtime_dict.values()),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Average Gini Index",
                    title="Concentrate GPA Average Gini Index",
                    data=list(graph_avg_gini_dict.values()),
                    y_lim=GraphAxisRange(
                        *metrics["AverageGiniIndex"].theoretical_range
                    ),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Minimum Gini Index",
                    title="Concentrate GPA Minimum Gini",
                    data=list(graph_min_gini_dict.values()),
                    y_lim=GraphAxisRange(*metrics["MinGiniIndex"].theoretical_range),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Maximum Gini Index",
                    title="Concentrate GPA Max Gini",
                    data=list(graph_max_gini_dict.values()),
                    y_lim=GraphAxisRange(*metrics["MaxGiniIndex"].theoretical_range),
                )
            )


if __name__ == "__main__":
    typer.run(ConcentrateGpaRun().start)
