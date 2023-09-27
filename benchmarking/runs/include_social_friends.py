import math

import typer

from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.utils.team_calculations import (
    is_happy_team_allhp_friend,
)
from benchmarking.evaluations.scenarios.include_social_friends import (
    IncludeSocialFriends,
)
from benchmarking.simulation.simulation import Simulation


def include_social_friends(num_trials: int = 10):
    """
    Goal: Run including social friends, measure average social satisfied team
    (a team socially satisfied when all member is happy)
    """

    # Defining our changing x-values (in the graph sense)
    class_sizes = [100, 150, 200, 250, 300]

    # Graph variables
    graph_data_dict = {}

    for class_size in class_sizes:
        print("CLASS SIZE /", class_size)

        number_of_teams = math.ceil(class_size / 5)

        # set up either mock or real data
        student_provider_settings = MockStudentProviderSettings(
            number_of_students=class_size,
            number_of_friends=2,
            number_of_enemies=2,
            friend_distribution="cluster",
        )

        simulation_outputs = Simulation(
            num_teams=number_of_teams,
            scenario=IncludeSocialFriends(),
            student_provider=MockStudentProvider(student_provider_settings),
            metrics=[
                AverageSocialSatisfaction(metric_function=is_happy_team_allhp_friend),
            ],
        ).run(num_runs=num_trials)

        average_runtimes = Simulation.average_metric(simulation_outputs, "runtimes")

        # Data processing for graph
        for algorithm_type, average_runtime in average_runtimes.items():
            if algorithm_type not in graph_data_dict:
                graph_data_dict[algorithm_type] = GraphData(
                    x_data=[class_size],
                    y_data=[average_runtime],
                    name=algorithm_type.value,
                )
            else:
                graph_data_dict[algorithm_type].x_data.append(class_size)
                graph_data_dict[algorithm_type].y_data.append(average_runtime)

    line_graph(
        LineGraphMetadata(
            x_label="Class size",
            y_label="Run time (seconds)",
            title="Simulate including friends",
            data=list(graph_data_dict.values()),
            description=None,
            y_lim=None,
            x_lim=None,
        )
    )


if __name__ == "__main__":
    typer.run(include_social_friends)
