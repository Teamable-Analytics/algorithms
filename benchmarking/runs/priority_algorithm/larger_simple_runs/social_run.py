import re
from os import path
from typing import Dict, Tuple, List

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    PriorityAlgorithmStartType,
)
from api.models.enums import (
    AlgorithmType,
)
from benchmarking.evaluations.graphing.graph_3d import graph_3d, Surface3D
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.metrics.utils.team_calculations import (
    is_strictly_happy_team_friend,
)
from benchmarking.evaluations.scenarios.include_social_friends import (
    IncludeSocialFriends,
)
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.larger_simple_runs.custom_student_providers import (
    Custom120SocialStudentProvider,
)
from benchmarking.runs.priority_algorithm.larger_simple_runs.run_utils import (
    get_pretty_metric_name,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class SocialRun(Run):
    CLASS_SIZE = 120
    NUMBER_OF_TEAMS = 30
    NUMBER_OF_STUDENTS_PER_TEAM = 4

    def start(self, num_trials: int = 30, generate_graphs: bool = False):
        # Ranges
        max_keep_range = [1] + list(range(5, 31, 5))
        max_spread_range = [1] + list(range(20, 101, 20))
        max_iterations_range = [1] + list(range(50, 251, 50))

        scenario = IncludeSocialFriends(
            max_num_friends=1,
            max_num_enemies=0,
        )

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
            "AverageSocialSatisfaction": AverageSocialSatisfaction(
                metric_function=is_strictly_happy_team_friend
            ),
        }

        start_types = [
            PriorityAlgorithmStartType.WEIGHT,
            PriorityAlgorithmStartType.RANDOM,
        ]

        artifacts_dict = {start_type: {} for start_type in start_types}
        for start_type in start_types:
            artifact: SimulationSetArtifact = SimulationSet(
                settings=SimulationSettings(
                    scenario=scenario,
                    student_provider=Custom120SocialStudentProvider(),
                    cache_key=f"priority_algorithm/larger_simple_runs/class_size_120/simple_social_run/",
                    num_teams=30,
                ),
                algorithm_set={
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_KEEP=max_keep,
                            MAX_SPREAD=max_spread,
                            MAX_ITERATE=max_iterations,
                            MAX_TIME=10000000,
                            START_TYPE=start_type,
                            name=f"max_keep_{max_keep}-max_spread_{max_spread}-max_iterations_{max_iterations}-{start_type.value}_start",
                        )
                        for max_keep in max_keep_range
                        for max_spread in max_spread_range
                        for max_iterations in max_iterations_range
                    ]
                },
            ).run(num_runs=num_trials)

            for name, simulation_artifact in artifact.items():
                match = re.search(
                    r"max_keep_(\d+)-max_spread_(\d+)-max_iterations_(\d+)",
                    name,
                )
                if match:
                    max_keep = int(match.group(1))
                    max_spread = int(match.group(2))
                    max_iterations = int(match.group(3))
                    artifacts_dict[start_type][
                        (max_keep, max_spread, max_iterations)
                    ] = simulation_artifact

        if generate_graphs:
            for metric_name, metric in metrics.items():
                points_dict = {}
                for start_type, artifacts in artifacts_dict.items():
                    points: Dict[Tuple[int, int, int], float] = {}
                    for point_location, simulation_artifact in artifacts.items():
                        insight_set = Insight.get_output_set(
                            artifact={"arbitrary_name": simulation_artifact},
                            metrics=[metric],
                        )
                        # Returns a dict[algorithm, value]
                        value_dict = Insight.average_metric(
                            insight_output_set=insight_set, metric_name=metric_name
                        )
                        # Get first value, assumes only one algorithm being run
                        value = list(value_dict.values())[0]
                        points[point_location] = value
                    points_dict[start_type] = points

                for max_iterations in max_iterations_range:
                    surfaces: List[Surface3D] = []
                    for start_type, points in points_dict.items():
                        surfaces.append(
                            Surface3D(
                                points=[
                                    (keep, spread, score)
                                    for (
                                        keep,
                                        spread,
                                        iterations,
                                    ), score in points.items()
                                    if iterations == max_iterations
                                ],
                                label=f"{start_type.value} start".title(),
                                color="blue" if start_type.value == "weight" else "red",
                            )
                        )
                    save_loc = path.abspath(
                        path.join(
                            path.dirname(__file__),
                            "graphs",
                            "social",
                            f"{get_pretty_metric_name(metric)} - {max_iterations} Iterations",
                        )
                    )
                    graph_3d(
                        surfaces,
                        graph_title=f"Priority Algorithm Parameters vs {get_pretty_metric_name(metric)}\n~Social Scenario, {max_iterations} iterations, 120 students~",
                        x_label="Max Keep",
                        y_label="Max Spread",
                        z_label=get_pretty_metric_name(metric),
                        z_lim=(0, 1),
                        invert_xaxis=True,
                        plot_legend=True,
                        save_graph=True,
                        filename=save_loc,
                    )


if __name__ == "__main__":
    typer.run(SocialRun().start)
