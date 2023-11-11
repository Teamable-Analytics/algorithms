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
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings


def include_social_friends(num_trials: int = 10, generate_graphs: bool = True):
    """
    Goal: Run including social friends, measure average social satisfied team
    (a team socially satisfied when all member is happy)
    """

    # Defining our changing x-values (in the graph sense)
    class_sizes = list(range(50, 501, 50))

    # Graph variables
    graph_runtime_dict = {}
    graph_social_sat_dict = {}
    graph_dicts = [graph_runtime_dict, graph_social_sat_dict]

    metrics: Dict[str, TeamSetMetric] = {
        "AverageSocialSatisfaction": AverageSocialSatisfaction(
            metric_function=is_happy_team_allhp_friend
        )
    }

    artifacts: Dict[int, SimulationSetArtifact] = {}

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

        simulation_set_artifact = SimulationSet(
            settings=SimulationSettings(
                num_teams=number_of_teams,
                scenario=IncludeSocialFriends(),
                student_provider=MockStudentProvider(student_provider_settings),
                cache_key=f"include_social_friends_{number_of_teams}",
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

            average_runtimes = Insight.average_metric(insight_set, Insight.KEY_RUNTIMES)
            average_social_satisfaction = Insight.average_metric(
                insight_set, "AverageSocialSatisfaction"
            )
            metric_values = [average_runtimes, average_social_satisfaction]

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
                title="Simulate including friends",
                data=list(graph_runtime_dict.values()),
            )
        )

        line_graph(
            LineGraphMetadata(
                x_label="Class size",
                y_label="Happy Team - Each Member Has One Friend On Team",
                title="Simulate including friends",
                data=list(graph_social_sat_dict.values()),
            )
        )


if __name__ == "__main__":
    typer.run(include_social_friends)
