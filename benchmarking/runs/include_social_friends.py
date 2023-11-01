import math
from typing import Dict, List

import typer

from api.models.enums import AlgorithmType
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.utils.team_calculations import (
    is_happy_team_allhp_friend,
)
from benchmarking.evaluations.scenarios.include_social_friends import (
    IncludeSocialFriends,
)
from benchmarking.simulation.basic_simulation_set_2 import BasicSimulationSet2
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_settings import SimulationSettings


def include_social_friends(num_trials: int = 10, generate_graphs: bool = False):
    """
    Goal: Run including social friends, measure average social satisfied team
    (a team socially satisfied when all member is happy)
    """

    # Defining our changing x-values (in the graph sense)
    class_sizes = [100, 150, 200, 250, 300]

    # Graph variables
    graph_runtime_dict = {}
    graph_social_sat_dict = {}
    graph_dicts = [graph_runtime_dict, graph_social_sat_dict]

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

        metrics: Dict[str:TeamSetMetric] = {
            "AverageSocialSatisfaction": AverageSocialSatisfaction(
                metric_function=is_happy_team_allhp_friend
            )
        }

        simulation_set_artifact = BasicSimulationSet2(
            settings=SimulationSettings(
                num_teams=number_of_teams,
                scenario=IncludeSocialFriends(),
                student_provider=MockStudentProvider(student_provider_settings),
                cache_key=f"include_social_friends_{number_of_teams}",
            )
        ).run(num_runs=num_trials)

        if generate_graphs:
            insight_set: Dict[
                AlgorithmType, Dict[str, List[float]]
            ] = Insight.get_output_set(
                artifact=simulation_set_artifact, metrics=list(metrics.values())
            )

            average_runtimes = Insight.average_metric(insight_set, Insight.KEY_RUNTIMES)
            average_social_satisfaction = Insight.average_metric(
                insight_set, "AverageSocialSatisfaction"
            )
            metric_values = [average_runtimes, average_social_satisfaction]

            # Data processing for graph
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
                title="Simulate including friends",
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
                y_label="Average Social Satisfaction",
                title="Simulate including friends",
                data=list(graph_social_sat_dict.values()),
                description=None,
                y_lim=None,
                x_lim=None,
                num_minor_ticks=None,
            )
        )


if __name__ == "__main__":
    typer.run(include_social_friends)
