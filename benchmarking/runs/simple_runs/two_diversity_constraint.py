import re
from typing import Dict, Tuple, List

import numpy as np
import typer
from matplotlib import pyplot as plt, cm

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.models.enums import (
    AlgorithmType,
    Gender,
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
    Gpa,
)
from api.models.tokenization_constraint import TokenizationConstraint
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.runs.interfaces import Run
from benchmarking.runs.simple_runs._data import SimpleRunData as data
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation import SimulationArtifact
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class TwoDiversityConstraint(Run):
    def start(self, num_trials: int = 1, generate_graphs: bool = True):
        scenario = TwoDiversityConstraintScenario(
            value_of_female=Gender.FEMALE.value, value_of_a=Gpa.A.value
        )
        metrics = data.get_metrics(scenario)
        artifact: SimulationSetArtifact = SimulationSet(
            settings=SimulationSettings(
                num_teams=data.num_teams,
                scenario=scenario,
                student_provider=data.student_provider,
                cache_key=f"priority_algorithm/simple_runs/two_diversity_constraint/",
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
                    for max_keep in data.max_keep_range
                    for max_spread in data.max_spread_range
                    for max_iterations in data.max_iterations_range
                ]
            },
        ).run(num_runs=num_trials)

        artifacts_dict: Dict[Tuple[int, int, int], SimulationArtifact] = {}
        for name, simulation_artifact in artifact.items():
            match = re.search(
                r"max_spread_(\d+)-max_keep_(\d+)-max_iterate_(\d+)", name
            )
            if match:
                max_keep = int(match.group(1))
                max_spread = int(match.group(2))
                max_iterations = int(match.group(3))
                artifacts_dict[
                    (max_keep, max_spread, max_iterations)
                ] = simulation_artifact

        if generate_graphs:
            points: Dict[Tuple[int, int, int], float] = {}
            for metric_name, metric in metrics.items():
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

                wireframe = True
                for max_iterations in data.max_iterations_range:
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
                    surface = (
                        ax.plot_wireframe(
                            X,
                            Y,
                            Z,
                            color="red",
                        )
                        if wireframe
                        else ax.plot_surface(
                            X,
                            Y,
                            Z,
                            cmap=cm.coolwarm,
                            linewidth=0,
                            antialiased=False,
                        )
                    )

                    if not wireframe:
                        fig.colorbar(surface, shrink=0.5, aspect=8, pad=0.15)

                    ax.set_title(
                        f"Priority Algorithm Parameters vs Priorities Satisfied\n~Two Diversity Constraint~\n~{max_iterations} iterations~"
                    )
                    ax.set_xlabel("MAX_KEEP")
                    ax.set_ylabel("MAX_SPREAD")
                    ax.set_zlabel("Score")
                    ax.set_zlim(np.min(Z), np.max(Z))
                    plt.show()


class TwoDiversityConstraintScenario(Scenario):
    def __init__(self, value_of_female: int, value_of_a: int):
        self.value_of_female = value_of_female
        self.value_of_a = value_of_a

    @property
    def name(self):
        return "Diversify on gender with a minimum of 2 female"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GENDER.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_female,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GPA.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_a,
                ),
            ),
            WeightGoal(diversity_goal_weight=1),
        ]


if __name__ == "__main__":
    typer.run(TwoDiversityConstraint().start)
