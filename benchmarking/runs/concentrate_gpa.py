import math

import typer

from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.metrics.average_gini_index import AverageGiniIndex
from benchmarking.evaluations.metrics.maximum_gini_index import MaximumGiniIndex
from benchmarking.evaluations.metrics.minimum_gini_index import MinimumGiniIndex
from benchmarking.evaluations.scenarios.concentrate_gpa import ConcentrateGPA
from benchmarking.simulation.simulation import Simulation
from models.enums import ScenarioAttribute, Gpa


def concentrate_gpa(num_trials: int = 10):
    """
    Goal: Run concentrate GPA scenario, and measure the average, maximum, and minimum gini scores for gpa
    """

    # Define changing values
    class_sizes = [50, 100, 150, 200, 250, 300, 350, 400]
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

        simulation_outputs = Simulation(
            num_teams=number_of_teams,
            scenario=ConcentrateGPA(),
            student_provider=MockStudentProvider(student_provider_settings),
            metrics=[
                AverageGiniIndex(attribute=ScenarioAttribute.GPA.value),
                MaximumGiniIndex(attribute=ScenarioAttribute.GPA.value),
                MinimumGiniIndex(attribute=ScenarioAttribute.GPA.value),
            ],
        ).run(num_runs=num_trials)

        average_ginis = Simulation.average_metric(
            simulation_outputs, "AverageGiniIndex"
        )
        maximum_ginis = Simulation.average_metric(
            simulation_outputs, "MaximumGiniIndex"
        )
        minimum_ginis = Simulation.average_metric(
            simulation_outputs, "MinimumGiniIndex"
        )
        average_runtimes = Simulation.average_metric(
            simulation_outputs, Simulation.KEY_RUNTIMES
        )
        metrics = [average_runtimes, average_ginis, minimum_ginis, maximum_ginis]

        # Data processing for graph
        for i, metric in enumerate(metrics):
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

    line_graph(
        LineGraphMetadata(
            x_label="Class size",
            y_label="Run time (seconds)",
            title="Concentrate GPA Runtimes",
            data=list(graph_runtime_dict.values()),
            description=None,
            y_lim=None,
            x_lim=None,
        )
    )

    line_graph(
        LineGraphMetadata(
            x_label="Class size",
            y_label="Average Gini Index",
            title="Concentrate GPA Average Gini Index",
            data=list(graph_avg_gini_dict.values()),
            description=None,
            y_lim=None,
            x_lim=None,
        )
    )

    line_graph(
        LineGraphMetadata(
            x_label="Class size",
            y_label="Minimum Gini Index",
            title="Concentrate GPA Minimum Gini",
            data=list(graph_min_gini_dict.values()),
            description=None,
            y_lim=None,
            x_lim=None,
        )
    )

    line_graph(
        LineGraphMetadata(
            x_label="Class size",
            y_label="Maximum Gini Index",
            title="Concentrate GPA Max Gini",
            data=list(graph_max_gini_dict.values()),
            description=None,
            y_lim=None,
            x_lim=None,
        )
    )


if __name__ == "__main__":
    typer.run(concentrate_gpa)
