from typing import Dict, List

import typer

from api.ai.interfaces.algorithm_config import (
    WeightAlgorithmConfig,
    SocialAlgorithmConfig,
    RandomAlgorithmConfig,
    AlgorithmConfig,
)
from api.models.enums import AlgorithmType
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProviderSettings,
    MockStudentProvider,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.utils.team_calculations import *
from benchmarking.evaluations.scenarios.give_the_people_what_they_want import (
    GiveThePeopleWhatTheyWant,
)
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.insight import Insight, InsightOutput
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings


class VariedNumFriendsSocialRun(Run):
    @staticmethod
    def start(num_trials: int = 1, generate_graphs: bool = True):
        """
        Goal: See how the social algorithm reacts to different numbers of friends.

        This run holds the team size constant at 4, then tests it with cliques that are 0.5, 1,
        1.5, and 2 times the size of the team. This will test to see if the algorithm will be
        able to put cliques into teams if the clique size does not match the team size.
        The most interesting case will be the 0.5 case because it should be able to put two
        full cliques into a single team.
        """

        clique_sizes = [2, 4, 6, 8]
        class_sizes = [100, 200]  # list(range(50, 501, 50))

        metrics: Dict[str, TeamSetMetric] = {
            "Strictly Happy Team (Friend)": AverageSocialSatisfaction(
                metric_function=is_strictly_happy_team_friend,
                name="Strictly Happy Team (Friend)",
            ),
            "Strictly Happy Team (Enemy)": AverageSocialSatisfaction(
                metric_function=is_strictly_happy_team_enemy,
                name="Strictly Happy Team (Enemy)",
            ),
            "Happy Team 1SHP (Friend)": AverageSocialSatisfaction(
                metric_function=is_happy_team_1shp_friend,
                name="Happy Team 1SHP (Friend)",
            ),
            "Happy Team 1SHP (Enemy)": AverageSocialSatisfaction(
                metric_function=is_happy_team_1shp_enemy,
                name="Happy Team 1SHP (Enemy)",
            ),
            "Happy Team 1HP (Friend)": AverageSocialSatisfaction(
                metric_function=is_happy_team_1hp_friend,
                name="Happy Team 1HP (Friend)",
            ),
            "Happy Team 1HP (Enemy)": AverageSocialSatisfaction(
                metric_function=is_happy_team_1hp_enemy,
                name="Happy Team 1HP (Enemy)",
            ),
            "Happy Team All HP (Friend)": AverageSocialSatisfaction(
                metric_function=is_happy_team_allhp_friend,
                name="Happy Team All HP (Friend)",
            ),
            "Happy Team All HP (Enemy)": AverageSocialSatisfaction(
                metric_function=is_happy_team_allhp_enemy,
                name="Happy Team All HP (Enemy)",
            ),
        }

        algorithms: Dict[AlgorithmType, List[AlgorithmConfig]] = {
            AlgorithmType.RANDOM: [RandomAlgorithmConfig()],
            AlgorithmType.WEIGHT: [WeightAlgorithmConfig()],
            AlgorithmType.SOCIAL: [SocialAlgorithmConfig()],
        }

        # Use: simulation_sets[clique_size][class_size]: SimulationSetArtifact
        simulation_sets: Dict[int, Dict[int, SimulationSetArtifact]] = {}

        for clique_size in clique_sizes:
            simulation_sets[clique_size] = {}
            for class_size in class_sizes:
                print(
                    f"Running with {class_size} students with {clique_size} friend{'s' if clique_size != 1 else ''}..."
                )

                student_provider_settings = MockStudentProviderSettings(
                    number_of_students=class_size,
                    number_of_friends=(clique_size - 1),
                    number_of_enemies=2,
                    friend_distribution="cluster",
                )

                simulation_sets[clique_size][class_size] = SimulationSet(
                    settings=SimulationSettings(
                        num_teams=class_size // 4,
                        scenario=GiveThePeopleWhatTheyWant(),
                        student_provider=MockStudentProvider(student_provider_settings),
                        cache_key=f"social/varied_num_friends/clique_size_{clique_size}/{class_size}_students",
                    ),
                    algorithm_set=algorithms,
                ).run(num_runs=num_trials)

        if generate_graphs:
            # Use: graph_data[clique_size][metric.name][algorithm_name] = GraphData
            graph_data: Dict[int, Dict[str, Dict[str, GraphData]]] = {}

            for clique_size in clique_sizes:
                graph_data[clique_size] = {}
                for class_size in class_sizes:
                    artifact: SimulationSetArtifact = simulation_sets[clique_size][
                        class_size
                    ]
                    insight_set: Dict[str, InsightOutput] = Insight.get_output_set(
                        artifact=artifact, metrics=list(metrics.values())
                    )

                    average_metrics: Dict[str, Dict[str, float]] = {}
                    for metric_name in [Insight.KEY_RUNTIMES, *metrics.keys()]:
                        average_metrics[metric_name] = Insight.average_metric(
                            insight_set, metric_name
                        )

                    for metric_name, average_metric in average_metrics.items():
                        if metric_name not in graph_data[clique_size]:
                            graph_data[clique_size][metric_name] = {}
                        for algorithm_name, value in average_metric.items():
                            if (
                                algorithm_name
                                not in graph_data[clique_size][metric_name]
                            ):
                                graph_data[clique_size][metric_name][
                                    algorithm_name
                                ] = GraphData(
                                    x_data=[class_size],
                                    y_data=[value],
                                    name=algorithm_name,
                                )
                            else:
                                graph_data[clique_size][metric_name][
                                    algorithm_name
                                ].x_data.append(class_size)
                                graph_data[clique_size][metric_name][
                                    algorithm_name
                                ].y_data.append(value)

            for metric_name in [Insight.KEY_RUNTIMES, *list(metrics.keys())]:
                for clique_size in clique_sizes:
                    y_label = (
                        "Run time (seconds)"
                        if metric_name == Insight.KEY_RUNTIMES
                        else "Ratio of Teams"
                    )
                    y_lim = (
                        None
                        if metric_name == Insight.KEY_RUNTIMES
                        else GraphAxisRange(-0.1, 1.1)
                    )
                    graph_subtitle = f"{metric_name.capitalize()} - Cliques {clique_size / 4}x team size"
                    graph_filename = f"varied_num_friends/clique_size_{clique_size}/{metric_name.lower().replace(' ', '_')}"
                    line_graph(
                        LineGraphMetadata(
                            x_label="Number of Friends",
                            y_label=y_label,
                            title="Varied Number of Friends",
                            description=graph_subtitle,
                            data=list(graph_data[clique_size][metric_name].values()),
                            y_lim=y_lim,
                            save_graph=True,
                            file_name=graph_filename,
                        )
                    )


if __name__ == "__main__":
    typer.run(VariedNumFriendsSocialRun.start)
