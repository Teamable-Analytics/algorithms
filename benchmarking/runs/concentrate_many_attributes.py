import math
from typing import Dict, List

import typer

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
from api.models.enums import ScenarioAttribute, Gender, Race, AlgorithmType
from benchmarking.simulation.basic_simulation_set_2 import BasicSimulationSet2
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_settings import SimulationSettings


def concentrate_many_attributes(num_trials: int = 10, generate_graphs: bool = False):
    """
    Goal: Run concentrate on many attributes scenario (6 attributes), measure average gini index across many attributes
    """

    # Defining our changing x-values (in the graph sense)
    class_sizes = list(range(50, 601, 50))
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

        simulation_set_artifact = BasicSimulationSet2(
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
            )
        ).run(num_runs=num_trials)

        if generate_graphs:
            insight_set: Dict[
                AlgorithmType, Dict[str, List[float]]
            ] = Insight.get_output_set(
                artifact=simulation_set_artifact, metrics=list(metrics.values())
            )

            average_gini = Insight.average_metric(
                insight_set, "AverageGiniIndexMultiAttribute"
            )
            average_runtimes = Insight.average_metric(insight_set, Insight.KEY_RUNTIMES)
            metric_values = [average_runtimes, average_gini]

            for i, metric in enumerate(metric_values):
                for algorithm_type, data in metric.items():
                    if algorithm_type not in graph_dicts[i]:
                        graph_dicts[i][algorithm_type] = GraphData(
                            x_data=[class_size],
                            y_data=[data],
                            name=algorithm_type.value,
                        )
                    else:
                        graph_dicts[i][algorithm_type].x_data.append(class_size)
                        graph_dicts[i][algorithm_type].y_data.append(data)

    if generate_graphs:
        line_graph(
            LineGraphMetadata(
                x_label="Class size",
                y_label="Run time (seconds)",
                title="Concentrate Many Attributes Runtimes",
                data=list(graph_runtime_dict.values()),
                description=None,
                y_lim=None,
                x_lim=None,
                num_minor_ticks=None,
            )
        )

        line_graph(
            LineGraphMetadata(
                x_label="Class size",
                y_label="Average Gini Index",
                title="Concentrate Many Attributes Average Gini Index",
                data=list(graph_avg_gini_dict.values()),
                description=None,
                y_lim=GraphAxisRange(
                    *metrics["AverageGiniIndexMulti"].theoretical_range
                ),
                x_lim=None,
                num_minor_ticks=None,
            )
        )


if __name__ == "__main__":
    typer.run(concentrate_many_attributes)
