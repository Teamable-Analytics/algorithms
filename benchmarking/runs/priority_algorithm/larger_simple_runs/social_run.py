import re
from typing import Dict, Tuple

import numpy as np
import typer
from matplotlib import pyplot as plt

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
)
from api.models.enums import (
    AlgorithmType,
)
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.metrics.utils.team_calculations import (
    is_happy_team_1hp_friend,
)
from benchmarking.evaluations.scenarios.include_social_friends import (
    IncludeSocialFriends,
)
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.larger_simple_runs.custom_student_providers import (
    Custom120SocialStudentProvider,
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
        max_spread_range = [1] + list(range(5, 31, 5))
        max_iterations_range = [1, 5, 10, 20, 30]

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
                metric_function=is_happy_team_1hp_friend
            ),
        }

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
                        name=f"max_keep_{max_keep}-max_spread_{max_spread}-max_iterations_{max_iterations}",
                    )
                    for max_keep in max_keep_range
                    for max_spread in max_spread_range
                    for max_iterations in max_iterations_range
                ]
            },
        ).run(num_runs=num_trials)

        artifacts_dict = {}
        for name, simulation_artifact in artifact.items():
            match = re.search(
                r"max_keep_(\d+)-max_spread_(\d+)-max_iterations_(\d+)",
                name,
            )
            if match:
                max_keep = int(match.group(1))
                max_spread = int(match.group(2))
                max_iterations = int(match.group(3))
                artifacts_dict[
                    (max_keep, max_spread, max_iterations)
                ] = simulation_artifact

        if generate_graphs:
            for metric_name, metric in metrics.items():
                points: Dict[Tuple[int, int, int], float] = {}
                for point_location, simulation_artifact in artifacts_dict.items():
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

                for max_iterations in max_iterations_range:
                    fig = plt.figure()
                    ax = fig.add_subplot(projection="3d")

                    # Filter
                    plotted_points = [
                        (keep, spread, score)
                        for (keep, spread, iterations), score in points.items()
                        if iterations == max_iterations
                    ]

                    # Format data
                    plotted_points = np.array(plotted_points)
                    x = plotted_points[:, 0]
                    y = plotted_points[:, 1]
                    unique_x = np.unique(x)
                    unique_y = np.unique(y)
                    X, Y = np.meshgrid(unique_x, unique_y)
                    Z = np.zeros_like(X)
                    for xi, yi, zi in plotted_points:
                        Z[
                            np.where(unique_y == yi)[0][0],
                            np.where(unique_x == xi)[0][0],
                        ] = zi

                    ##### \/ \/ \/ \/ TEMP. REMOVE LATER \/ \/ \/ \/ #####
                    remove_missing_points = False
                    if remove_missing_points:
                        # Find the index where the first zero appears in each row
                        zero_indices = np.argmax(Z == 0, axis=1)

                        # Find the index where the first zero appears in any row
                        first_zero_index = np.argmax(zero_indices > 0)

                        # Remove rows with zeros
                        X = X[:first_zero_index, :]
                        Y = Y[:first_zero_index, :]
                        Z = Z[:first_zero_index, :]

                    ##### /\ /\ /\ /\ TEMP. REMOVE LATER /\ /\ /\ /\ #####

                    # Plot the surface
                    surface = ax.plot_wireframe(
                        X,
                        Y,
                        Z,
                        color=("blue"),
                    )

                    ax.set_title(
                        f"Priority Algorithm Parameters vs {metric_name.title()}\n~Social Scenario, {max_iterations} iterations, 120 students~"
                    )
                    ax.set_xlabel("MAX_KEEP")
                    ax.set_ylabel("MAX_SPREAD")
                    ax.set_zlabel("Score")
                    ax.set_zlim(0, 1)
                    plt.show()


if __name__ == "__main__":
    typer.run(SocialRun().start)
