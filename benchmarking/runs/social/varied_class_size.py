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


class VariedClassSizeSocialRun(SocialRun):
    @staticmethod
    def start(num_trials: int = 10, generate_graphs: bool = False):
        """
        Goal: See how the social algorithm does as the class size gets larger
        """

        class_sizes = list(range(50, 601, 50))

        # Use: simulation_sets[clique_size]: SimulationSetArtifact
        simulation_sets: Dict[int, SimulationSetArtifact] = {}

        for class_size in class_sizes:
            print(f"Running with {class_size} students...")

            student_provider_settings = MockStudentProviderSettings(
                number_of_students=class_size,
                number_of_friends=4,
                number_of_enemies=2,
                friend_distribution="cluster",
            )

            simulation_sets[class_size] = SimulationSet(
                settings=SimulationSettings(
                    num_teams=class_size // 5,
                    scenario=IncludeFriendsExcludeEnemies(),
                    student_provider=MockStudentProvider(student_provider_settings),
                    cache_key=f"social/varied_class_size/{class_size}_students",
                ),
                algorithm_set=SocialRun.algorithms(),
            ).run(num_runs=num_trials)

        if generate_graphs:
            # Use: graph_data[metric.name][algorithm_name] = GraphData
            graph_data: Dict[str, Dict[str, GraphData]] = {}

            for class_size in class_sizes:
                artifact: SimulationSetArtifact = simulation_sets[class_size]
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
                                x_data=[class_size],
                                y_data=[value],
                                name=algorithm_name,
                            )
                        else:
                            graph_data[metric_name][algorithm_name].x_data.append(
                                class_size
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
                    f"varied_class_size/{metric_name.lower().replace(' ', '_')}"
                )
                line_graph(
                    LineGraphMetadata(
                        x_label="Class Size",
                        y_label=y_label,
                        title="Varied Class Size",
                        description=graph_subtitle,
                        data=list(graph_data[metric_name].values()),
                        y_lim=y_lim,
                        save_graph=True,
                        file_name=graph_filename,
                    )
                )


if __name__ == "__main__":
    typer.run(VariedClassSizeSocialRun.start)
