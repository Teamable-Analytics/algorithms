import math

import typer

from benchmarking.evaluations.goals import DiversityGoal
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.metrics.maximum_gini_index import MaximumGiniIndex
from benchmarking.evaluations.metrics.minimum_gini_index import MinimumGiniIndex
from api.models.enums import ScenarioAttribute, Gender
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.metrics.average_gini_index import (
    AverageGiniIndex,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.diversify_gender_min_2_female import (
    DiversifyGenderMin2Female,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.simulation import Simulation


def diversify_gender_min_2(num_trials: int = 10):
    """
    Goal: Run diversify gender scenario, measure average, min, and max gini index
    """

    # Defining our changing x-values (in the graph sense)
    class_sizes = list(range(50, 401, 50))
    num_trials = 10
    ratio_of_female_students = 0.2

    graph_runtime_dict = {}
    graph_avg_gini_dict = {}
    graph_min_gini_dict = {}
    graph_max_gini_dict = {}
    graph_priority_dict = {}
    graph_dicts = [
        graph_runtime_dict,
        graph_avg_gini_dict,
        graph_min_gini_dict,
        graph_max_gini_dict,
        graph_priority_dict,
    ]

    for class_size in class_sizes:
        print("CLASS SIZE /", class_size)

        number_of_teams = math.ceil(class_size / 5)

        # set up either mock or real data
        student_provider_settings = MockStudentProviderSettings(
            number_of_students=class_size,
            attribute_ranges={
                ScenarioAttribute.GENDER.value: [
                    (Gender.MALE, 1 - ratio_of_female_students),
                    (Gender.FEMALE, ratio_of_female_students),
                ],
            },
        )

        scenario = DiversifyGenderMin2Female(value_of_female=Gender.FEMALE.value)

        simulation_outputs = Simulation(
            num_teams=number_of_teams,
            scenario=scenario,
            student_provider=MockStudentProvider(student_provider_settings),
            metrics=[
                AverageGiniIndex(attribute=ScenarioAttribute.GENDER.value),
                MaximumGiniIndex(attribute=ScenarioAttribute.GENDER.value),
                MinimumGiniIndex(attribute=ScenarioAttribute.GENDER.value),
                PrioritySatisfaction(
                    goals_to_priorities(
                        [
                            goal
                            for goal in scenario.goals
                            if isinstance(goal, DiversityGoal)
                        ]
                    ),
                    False,
                ),
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
        satisfied_priorities = Simulation.average_metric(
            simulation_outputs, "PrioritySatisfaction"
        )
        metrics = [
            average_runtimes,
            average_ginis,
            minimum_ginis,
            maximum_ginis,
            satisfied_priorities,
        ]

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
            title="Diversity Gender With Min of Two Runtimes",
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
            title="Diversity Gender With Min of Two Average Gini Index",
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
            title="Diversity Gender With Min of Two Minimum Gini",
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
            title="Diversity Gender With Min of Two Max Gini",
            data=list(graph_max_gini_dict.values()),
            description=None,
            y_lim=None,
            x_lim=None,
        )
    )

    line_graph(
        LineGraphMetadata(
            x_label="Class size",
            y_label="Priorities Satisfied",
            title="Diversity Gender With Min of Two Satisfied Priorities",
            data=list(graph_priority_dict.values()),
            description=None,
            y_lim=None,
            x_lim=None,
        )
    )


if __name__ == "__main__":
    typer.run(diversify_gender_min_2)
