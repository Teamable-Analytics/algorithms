import math

from benchmarking.data.interfaces import MockStudentProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProvider
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.metrics.average_gini_index import AverageGiniIndex
from benchmarking.evaluations.metrics.maximum_gini_index import MaximumGiniIndex
from benchmarking.evaluations.metrics.minimum_gini_index import MinimumGiniIndex
from benchmarking.evaluations.scenarios.concentrate_gpa import ConcentrateGPA
from benchmarking.simulation.simulation import Simulation
from models.enums import ScenarioAttribute, Gpa


def concentrate_gpa_run():
    """
    Goal: Run concentrate GPA scenario, and measure the average, maximum, and minimum gini scores for gpa
    """

    # Define changing values
    class_sizes = [50, 150, 200, 250, 300]
    num_trials = 10
    ratio_of_a_students = 0.25
    ratio_of_b_students = 0.50
    ratio_of_c_students = 0.25

    # Graph variables
    graph_data_dict = {}

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

        print(
            "Average Gini Index for GPA =>",
            Simulation.average_metric(simulation_outputs, "AverageGiniIndex"),
        )
        print(
            "Maximum Gini Index for GPA =>",
            Simulation.average_metric(simulation_outputs, "MaximumGiniIndex"),
        )
        print(
            "Minimum Gini Index for GPA =>",
            Simulation.average_metric(simulation_outputs, "MinimumGiniIndex"),
        )

        average_ginis = Simulation.average_metric(simulation_outputs, "AverageGiniIndex")
        maximum_ginis = Simulation.average_metric(simulation_outputs, "MaximumGiniIndex")
        minimum_ginis = Simulation.average_metric(simulation_outputs, "MinimumGiniIndex")

        # Data processing for graph
        for algorithm_type, average_gini in average_ginis.items():
            if algorithm_type not in graph_data_dict:
                graph_data_dict[algorithm_type] = GraphData(
                    x_data=[class_size],
                    y_data=[average_gini],
                    name=algorithm_type.value,
                )
            else:
                graph_data_dict[algorithm_type].x_data.append(class_size)
                graph_data_dict[algorithm_type].y_data.append(average_gini)

    line_graph(
        LineGraphMetadata(
            x_label="Class size",
            y_label="Average gini Index",
            title="Concentrate GPA Results",
            data=list(graph_data_dict.values()),
            description=None,
            y_lim=None,
            x_lim=None,
        )
    )


if __name__ == "__main__":
    concentrate_gpa_run()
