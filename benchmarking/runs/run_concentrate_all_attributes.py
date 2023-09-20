import math

from benchmarking.data.interfaces import MockStudentProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.metrics.average_gini_index_multi_attribute import (
    AverageGiniIndexMultiAttribute,
)
from benchmarking.evaluations.scenarios.concentrate_all_attributes import (
    ConcentrateAllAttributes,
)
from benchmarking.simulation.simulation import Simulation
from models.enums import ScenarioAttribute, Gender, Race


def run_concentrate_all_attributes():
    """
    Goal: Run concentrate all attributes scenario, measure average gini index across all attributes
    """

    # Defining our changing x-values (in the graph sense)
    class_sizes = list(range(50, 601, 50))
    num_trials = 10
    ratio_of_female_students = 0.5

    graph_runtime_dict = {}
    graph_avg_gini_dict = {}
    graph_dicts = [
        graph_runtime_dict,
        graph_avg_gini_dict,
    ]

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
            num_values_per_attribute={
                ScenarioAttribute.PROJECT_PREFERENCES.value: 3,
            },
        )

        simulation_outputs = Simulation(
            num_teams=number_of_teams,
            scenario=ConcentrateAllAttributes(),
            student_provider=MockStudentProvider(student_provider_settings),
            metrics=[
                AverageGiniIndexMultiAttribute(
                    attributes=[
                        ScenarioAttribute.AGE.value,
                        ScenarioAttribute.GENDER.value,
                        ScenarioAttribute.GPA.value,
                        ScenarioAttribute.RACE.value,
                        ScenarioAttribute.MAJOR.value,
                        ScenarioAttribute.YEAR_LEVEL.value,
                    ]
                ),
            ],
        ).run(num_runs=num_trials)

        average_gini = Simulation.average_metric(
            simulation_outputs, "AverageGiniIndexMultiAttribute"
        )

        average_runtimes = Simulation.average_metric(
            simulation_outputs, Simulation.KEY_RUNTIMES
        )

        metrics = [average_runtimes, average_gini]

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
            title="Concentrate Many Attributes Runtimes",
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
            title="Concentrate Many Attributes Average Gini Index",
            data=list(graph_avg_gini_dict.values()),
            description=None,
            y_lim=GraphAxisRange(0, 1),
            x_lim=None,
        )
    )


if __name__ == "__main__":
    run_concentrate_all_attributes()
