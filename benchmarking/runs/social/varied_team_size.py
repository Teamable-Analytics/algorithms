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


class VariedTeamSizeSocialRun(Run):
    @staticmethod
    def start(num_trials: int = 10, generate_graphs: bool = True):
        """
        Goal: See how the social algorithm reacts to different team sizes.
        We will keep the number of friends (clique size) equal to the team size as that is
        the most likely scenario in a class setting and allows us to see the effect of the
        algorithm trying to deal with larger cliques without having to worry about them
        not fitting into a single team.
        """

        # Use team sizes that will evenly divide the class sizes
        team_sizes = [
            2,
            4,
            5,
            8,
            10,
        ]
        class_sizes = [200, 400]

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

        # Use: simulation_sets[class_size][team_size]: SimulationSetArtifact
        simulation_sets: Dict[int, Dict[int, SimulationSetArtifact]] = {}

        for class_size in class_sizes:
            simulation_sets[class_size] = {}
            for team_size in team_sizes:
                print(
                    f"Running with {class_size} students split into teams of {team_size}..."
                )

                num_teams = class_size // team_size

                # Number of enemies can stay constant because it is a relatively easy constraint to reach, especially with such a large class size
                student_provider_settings = MockStudentProviderSettings(
                    number_of_students=class_size,
                    number_of_friends=(team_size - 1),
                    number_of_enemies=2,
                    friend_distribution="cluster",
                )

                simulation_sets[class_size][team_size] = SimulationSet(
                    settings=SimulationSettings(
                        num_teams=num_teams,
                        scenario=GiveThePeopleWhatTheyWant(),
                        student_provider=MockStudentProvider(student_provider_settings),
                        cache_key=f"social/varied_team_size/{class_size}_students/team_size_{team_size}",
                    ),
                    algorithm_set=algorithms,
                ).run(num_runs=num_trials)

        if generate_graphs:
            # Use: graph_data[class_size][metric.name][algorithm_name] = GraphData
            graph_data: Dict[int, Dict[str, Dict[str, GraphData]]] = {}

            for class_size in class_sizes:
                graph_data[class_size] = {}
                for team_size in team_sizes:
                    artifact: SimulationSetArtifact = simulation_sets[class_size][
                        team_size
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
                        if metric_name not in graph_data[class_size]:
                            graph_data[class_size][metric_name] = {}
                        for algorithm_name, value in average_metric.items():
                            if (
                                algorithm_name
                                not in graph_data[class_size][metric_name]
                            ):
                                graph_data[class_size][metric_name][
                                    algorithm_name
                                ] = GraphData(
                                    x_data=[team_size],
                                    y_data=[value],
                                    name=algorithm_name,
                                )
                            else:
                                graph_data[class_size][metric_name][
                                    algorithm_name
                                ].x_data.append(team_size)
                                graph_data[class_size][metric_name][
                                    algorithm_name
                                ].y_data.append(value)

            for metric_name in [Insight.KEY_RUNTIMES, *list(metrics.keys())]:
                for class_size in class_sizes:
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
                    graph_subtitle = (
                        f"{metric_name.capitalize()} - {class_size} students"
                    )
                    graph_filename = f"varied_team_size/{class_size}_students/{metric_name.lower().replace(' ', '_')}"
                    line_graph(
                        LineGraphMetadata(
                            x_label="Team size",
                            y_label=y_label,
                            title=f"Varied Team Size",
                            description=graph_subtitle,
                            data=list(graph_data[class_size][metric_name].values()),
                            y_lim=y_lim,
                            save_graph=True,
                            file_name=graph_filename,
                        )
                    )


if __name__ == "__main__":
    typer.run(VariedTeamSizeSocialRun.start)
