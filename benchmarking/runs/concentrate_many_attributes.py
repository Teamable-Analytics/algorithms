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
from benchmarking.evaluations.metrics.average_gini_index_multi_attribute import (
    AverageGiniIndexMultiAttribute,
)
from benchmarking.evaluations.scenarios.concentrate_multiple_attributes import (
    ConcentrateMultipleAttributes,
)
from api.dataclasses.enums import ScenarioAttribute, Gender, Race, AlgorithmType
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class ConcentrateManyAttributesRun(Run):
    def start(self, num_trials: int = 10, generate_graphs: bool = True):
        """
        Goal: Run concentrate on many attributes scenario (6 attributes), measure average gini index across many attributes
        """

        # Defining our changing x-values (in the graph sense)
        class_sizes = list(range(50, 501, 50))
        ratio_of_female_students = 0.5

        graph_runtime_dict = {}
        graph_avg_gini_dict = {}
        graph_dicts = [
            graph_runtime_dict,
            graph_avg_gini_dict,
        ]

        metrics: Dict[str, TeamSetMetric] = {
            "AverageGiniIndexMulti": AverageGiniIndexMultiAttribute(
                attributes=[
                    ScenarioAttribute.AGE.value,
                    ScenarioAttribute.GENDER.value,
                    ScenarioAttribute.GPA.value,
                    ScenarioAttribute.RACE.value,
                    ScenarioAttribute.MAJOR.value,
                    ScenarioAttribute.YEAR_LEVEL.value,
                ]
            ),
        }
        artifacts: Dict[int, SimulationSetArtifact] = {}

        for class_size in class_sizes:
            print("CLASS SIZE /", class_size)

            number_of_teams = math.ceil(class_size / 5)

            # set up either mock or real data
            student_provider_settings = MockStudentProviderSettings(
                number_of_students=class_size,
                attribute_ranges={
                    ScenarioAttribute.AGE.value: list(range(20, 24)),
                    ScenarioAttribute.GENDER.value: [
                        (Gender.MALE, 1 - ratio_of_female_students),
                        (Gender.FEMALE, ratio_of_female_students),
                    ],
                    ScenarioAttribute.GPA.value: list(range(60, 100)),
                    ScenarioAttribute.RACE.value: list(range(len(Race))),
                    ScenarioAttribute.MAJOR.value: list(range(1, 4)),
                    ScenarioAttribute.YEAR_LEVEL.value: list(range(3, 5)),
                },
            )

            simulation_set_artifact = SimulationSet(
                settings=SimulationSettings(
                    num_teams=number_of_teams,
                    scenario=ConcentrateMultipleAttributes(
                        [
                            ScenarioAttribute.AGE,
                            ScenarioAttribute.GENDER,
                            ScenarioAttribute.GPA,
                            ScenarioAttribute.RACE,
                            ScenarioAttribute.MAJOR,
                            ScenarioAttribute.YEAR_LEVEL,
                        ]
                    ),
                    student_provider=MockStudentProvider(student_provider_settings),
                    cache_key=f"concentrate_many_attributes_{number_of_teams}",
                ),
                algorithm_set={
                    AlgorithmType.RANDOM: [RandomAlgorithmConfig()],
                    AlgorithmType.SOCIAL: [SocialAlgorithmConfig()],
                    AlgorithmType.WEIGHT: [WeightAlgorithmConfig()],
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(),
                        PriorityAlgorithmConfig(
                            name="local_max",
                            MUTATIONS=[(mutate_local_max, 1), (mutate_random_swap, 2)],
                        ),
                    ],
                },
            ).run(num_runs=num_trials)
            artifacts[class_size] = simulation_set_artifact

        if generate_graphs:
            for class_size, artifact in artifacts.items():
                insight_set: Dict[str, Dict[str, List[float]]] = Insight.get_output_set(
                    artifact=artifact, metrics=list(metrics.values())
                )
                average_gini = Insight.average_metric(
                    insight_set, "AverageGiniIndexMultiAttribute"
                )
                average_runtimes = Insight.average_metric(
                    insight_set, Insight.KEY_RUNTIMES
                )
                metric_values = [average_runtimes, average_gini]
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
                    title="Concentrate Many Attributes Runtimes",
                    data=list(graph_runtime_dict.values()),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Average Gini Index",
                    title="Concentrate Many Attributes Average Gini Index",
                    data=list(graph_avg_gini_dict.values()),
                    y_lim=GraphAxisRange(
                        *metrics["AverageGiniIndexMulti"].theoretical_range
                    ),
                )
            )


if __name__ == "__main__":
    typer.run(ConcentrateManyAttributesRun().start)
