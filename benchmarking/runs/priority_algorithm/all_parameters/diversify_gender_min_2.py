import os
import re
from typing import Dict, Tuple

import numpy as np
import typer
from matplotlib import pyplot as plt, cm

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.models.enums import Gender, ScenarioAttribute, AlgorithmType
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.diversify_gender_min_2_female import (
    DiversifyGenderMin2Female,
)
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation import SimulationArtifact
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings


class DiversifyGenderMin2(Run):
    RATIO_OF_FEMALE_STUDENT = 0.4

    def start(self, num_trials: int = 15, generate_graphs: bool = False):
        """
        Goal:
        - Need to create a run to generate all the data for max spread, max keep, and max iterations
        - Create a graph function to plot the data in 3D and generate the heat map
        - Need to rationalize bounds for each of the items in the plot (consider relationships between features)
        - We will be ignoring max time as it is just an arbitrary value we impose on the algorithm to reduce computation time
        """

        scenario = DiversifyGenderMin2Female(value_of_female=Gender.FEMALE.value)
        class_size = 100
        team_size = 5
        num_teams = class_size // team_size
        student_provider_settings = MockStudentProviderSettings(
            number_of_students=class_size,
            attribute_ranges={
                ScenarioAttribute.GENDER.value: [
                    (Gender.MALE, 1 - self.RATIO_OF_FEMALE_STUDENT),
                    (Gender.FEMALE, self.RATIO_OF_FEMALE_STUDENT),
                ],
            },
        )

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
        }

        # Ranges
        max_keep_range = [10, 500, 1000, 1500, 2000, 2500]
        max_spread_range = [1, 10, 20, 30, 40, 50]
        max_iterations_range = [10, 250, 500, 750, 1000]

        # Find completed simulations
        # completed_configs = []
        # files = os.listdir(
        #     os.path.join(
        #         os.path.dirname(__file__),
        #         "..",
        #         "..",
        #         "..",
        #         "..",
        #         "simulation_cache",
        #         "priority_algorithm",
        #         "all_parameters",
        #         "diversify_gender_min_2",
        #     )
        # )
        # for file in files:
        #     if file.endswith(".json"):
        #         match = re.match(
        #             r"AlgorithmType.PRIORITY-max_keep_(\d+)-max_spread_(\d+)-max_iterations_(\d+).json",
        #             file,
        #         )
        #         if match:
        #             max_keep = match.group(1)
        #             max_spread = match.group(2)
        #             max_iterations = match.group(3)
        #             completed_configs.append(
        #                 (int(max_keep), int(max_spread), int(max_iterations))
        #             )

        algorithm_set = {
            AlgorithmType.PRIORITY: [
                PriorityAlgorithmConfig(
                    MAX_KEEP=max_keep,
                    MAX_SPREAD=max_spread,
                    MAX_ITERATE=max_iterations,
                    MAX_TIME=10000000,
                    name=f"max_keep_{max_keep}-max_spread_{max_spread}-max_iterations_{max_iterations}_weight_start",
                )
                for max_keep in max_keep_range
                for max_spread in max_spread_range
                for max_iterations in max_iterations_range
                # if (max_keep, max_spread, max_iterations) in completed_configs
            ]
        }

        artifact: SimulationSetArtifact = SimulationSet(
            settings=SimulationSettings(
                num_teams=num_teams,
                scenario=scenario,
                student_provider=MockStudentProvider(student_provider_settings),
                cache_key=f"priority_algorithm/all_parameters/diversify_gender_min_2/",
            ),
            algorithm_set=algorithm_set,
        ).run(num_runs=num_trials)

        artifacts: Dict[Tuple[int, int, int], SimulationArtifact] = {}
        for name, simulation_artifact in artifact.items():
            match = re.search(
                r"max_keep_(\d+)-max_spread_(\d+)-max_iterations_(\d+)", name
            )
            if match:
                max_keep = int(match.group(1))
                max_spread = int(match.group(2))
                max_iterations = int(match.group(3))
                artifacts[(max_keep, max_spread, max_iterations)] = simulation_artifact

        if generate_graphs:
            # Process data and plot
            for metric_name, metric in metrics.items():
                # Dict with points[(x, y, z)] = avg metric value (between 0-1)
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

                wireframe = True
                for max_iterations in max_iterations_range:
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
                    fig = plt.figure()
                    ax = fig.add_subplot(projection="3d")
                    surface = (
                        ax.plot_wireframe(X, Y, Z)
                        if wireframe
                        else ax.plot_surface(
                            X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=False
                        )
                    )
                    if not wireframe:
                        fig.colorbar(surface, shrink=0.5, aspect=8, pad=0.15)

                    ax.set_title(
                        f"Priority Algorithm Parameters vs Priorities Satisfied\n~{max_iterations} iterations~"
                    )
                    ax.set_xlabel("MAX_KEEP")
                    ax.set_ylabel("MAX_SPREAD")
                    ax.set_zlabel("Score")
                    ax.set_zlim(np.min(Z), np.max(Z))
                    plt.show()


if __name__ == "__main__":
    typer.run(DiversifyGenderMin2().start)
