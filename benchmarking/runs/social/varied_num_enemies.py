from typing import Dict

import typer

from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProviderSettings,
    MockStudentProvider,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.scenarios.include_friends_exclude_enemies import (
    IncludeFriendsExcludeEnemies,
)
from benchmarking.runs.social.scoial_run import SocialRun
from benchmarking.simulation.insight import Insight, InsightOutput
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings


class VariedNumEnemiesSocialRun(SocialRun):
    @staticmethod
    def start(num_trials: int = 50, generate_graphs: bool = False):
        """
        Goal: See how the social algorithm reacts to different numbers of enemies.

        This run will hold the class size constant and show what happens as the number of
        enemies specified by each student changes. Cliques are equal in size to team size.
        """
        enemy_nums = list(range(0, 10))

        # Use: simulation_sets[num_friends]: SimulationSetArtifact
        simulation_sets: Dict[int, SimulationSetArtifact] = {}

        for num_enemies in enemy_nums:
            print(
                f"Running with {num_enemies} enem{'ies' if num_enemies != 1 else 'y'}..."
            )

            student_provider_settings = MockStudentProviderSettings(
                number_of_students=250,
                number_of_friends=5,
                number_of_enemies=num_enemies,
                friend_distribution="cluster",
            )

            simulation_sets[num_enemies] = SimulationSet(
                settings=SimulationSettings(
                    num_teams=250 // 5,
                    scenario=IncludeFriendsExcludeEnemies(),
                    student_provider=MockStudentProvider(student_provider_settings),
                    cache_key=f"social/varied_num_enemies/{num_enemies}_enemies",
                ),
                algorithm_set=SocialRun.algorithms(),
            ).run(num_runs=num_trials)

        if generate_graphs:
            # Use: graph_data[metric.name][algorithm_name] = GraphData
            graph_data: Dict[str, Dict[str, GraphData]] = {}

            for num_enemies in enemy_nums:
                artifact: SimulationSetArtifact = simulation_sets[num_enemies]
                insight_set: Dict[str, InsightOutput] = Insight.get_output_set(
                    artifact=artifact, metrics=list(SocialRun.metrics().values())
                )

                average_metrics: Dict[str, Dict[str, float]] = {}
                for metric_name in [Insight.KEY_RUNTIMES, *SocialRun.metrics().keys()]:
                    average_metrics[metric_name] = Insight.average_metric(
                        insight_set, metric_name
                    )

                for metric_name, average_metric in average_metrics.items():
                    if metric_name not in graph_data:
                        graph_data[metric_name] = {}
                    for algorithm_name, value in average_metric.items():
                        if algorithm_name not in graph_data[metric_name]:
                            graph_data[metric_name][algorithm_name] = GraphData(
                                x_data=[num_enemies],
                                y_data=[value],
                                name=algorithm_name,
                            )
                        else:
                            graph_data[metric_name][algorithm_name].x_data.append(
                                num_enemies
                            )
                            graph_data[metric_name][algorithm_name].y_data.append(value)

            for metric_name in [
                Insight.KEY_RUNTIMES,
                *list(SocialRun.metrics().keys()),
            ]:
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
                graph_subtitle = f"{metric_name.capitalize()}"
                graph_filename = (
                    f"varied_num_enemies/{metric_name.lower().replace(' ', '_')}"
                )
                line_graph(
                    LineGraphMetadata(
                        x_label="Number of Enemies",
                        y_label=y_label,
                        title="Varied Number of Enemies",
                        description=graph_subtitle,
                        data=list(graph_data[metric_name].values()),
                        y_lim=y_lim,
                        save_graph=True,
                        file_name=graph_filename,
                    )
                )


if __name__ == "__main__":
    typer.run(VariedNumEnemiesSocialRun.start)
