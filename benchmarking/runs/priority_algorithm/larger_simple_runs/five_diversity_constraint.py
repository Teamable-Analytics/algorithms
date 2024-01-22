import re
from typing import Dict, Tuple, List

import numpy as np
import typer
from matplotlib import pyplot as plt

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    PriorityAlgorithmStartType,
)
from api.models.enums import (
    AlgorithmType,
    Gender,
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
    Gpa,
    Race,
)
from api.models.tokenization_constraint import TokenizationConstraint
from benchmarking.data.interfaces import StudentProvider
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.larger_simple_runs.custom_student_providers import (
    CustomOneHundredAndTwentyStudentProvider,
    Major,
)
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings

from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.simulation.goal_to_priority import goals_to_priorities


class FiveDiversityConstraint(Run):
    def start(self, num_trials: int = 30, generate_graphs: bool = True):
        class_sizes = [120]
        num_teams = 30
        student_providers: Dict[int, StudentProvider] = {
            120: CustomOneHundredAndTwentyStudentProvider(),
        }

        def get_metrics(scenario: Scenario):
            return {
                "PrioritySatisfaction": PrioritySatisfaction(
                    goals_to_priorities(scenario.goals),
                    False,
                ),
            }

        # Ranges
        max_keep_range = [1] + list(range(5, 31, 5))
        max_spread_range = [1] + list(range(5, 31, 5))
        max_iterations_range = [
            1,
        ]  #  5, 10, 20, 30

        scenario = FiveDiversityConstraintScenario(
            value_of_female=Gender.FEMALE.value,
            value_of_a=Gpa.A.value,
            value_of_21=21,
            value_of_math=Major.MATH.value,
            value_of_european=Race.European.value,
        )
        metrics = get_metrics(scenario)
        start_types = [
            PriorityAlgorithmStartType.WEIGHT,
            PriorityAlgorithmStartType.RANDOM,
        ]

        artifacts_dict = {
            class_size: {start_type: {} for start_type in start_types}
            for class_size in class_sizes
        }
        for class_size in class_sizes:
            for start_type in start_types:
                artifact: SimulationSetArtifact = SimulationSet(
                    settings=SimulationSettings(
                        num_teams=num_teams,
                        scenario=scenario,
                        student_provider=student_providers[class_size],
                        cache_key=f"priority_algorithm/larger_simple_runs/class_size_{class_size}/five_diversity_constraint/25_buckets",
                    ),
                    algorithm_set={
                        AlgorithmType.PRIORITY: [
                            PriorityAlgorithmConfig(
                                MAX_KEEP=max_keep,
                                MAX_SPREAD=max_spread,
                                MAX_ITERATE=max_iterations,
                                MAX_TIME=1000001,
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
                        artifacts_dict[class_size][start_type][
                            (max_keep, max_spread, max_iterations)
                        ] = simulation_artifact

        if generate_graphs:
            for metric_name, metric in metrics.items():
                for class_size in class_sizes:
                    points_dict = {}
                    for start_type, artifacts in artifacts_dict[class_size].items():
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
                        fig = plt.figure()
                        ax = fig.add_subplot(projection="3d")
                        for start_type, points in points_dict.items():
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

                            # Plot the surface
                            surface = ax.plot_wireframe(
                                X,
                                Y,
                                Z,
                                color=(
                                    "blue" if start_type.value == "weight" else "red"
                                ),
                                label=f"{start_type.value} start".title(),
                            )

                        ax.set_title(
                            f"Priority Algorithm Parameters vs Priorities Satisfied\n~Five Diversity Constraint, {max_iterations} iterations, {class_size} students~"
                        )
                        ax.set_xlabel("MAX_KEEP")
                        ax.invert_xaxis()
                        ax.set_ylabel("MAX_SPREAD")
                        ax.set_zlabel("Score")
                        ax.set_zlim(0, 1)
                        plt.legend(
                            loc="lower left",
                            bbox_to_anchor=(1.2, 0.8),
                            borderaxespad=0,
                        )
                        plt.subplots_adjust(right=0.64)
                        plt.show()


class FiveDiversityConstraintScenario(Scenario):
    def __init__(
        self,
        value_of_female: int,
        value_of_a: int,
        value_of_21: int,
        value_of_math: int,
        value_of_european: int,
    ):
        self.value_of_female = value_of_female
        self.value_of_a = value_of_a
        self.value_of_21 = value_of_21
        self.value_of_math = value_of_math
        self.value_of_european = value_of_european

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
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.AGE.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_21,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.MAJOR.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_math,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.RACE.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_european,
                ),
            ),
            WeightGoal(diversity_goal_weight=1),
        ]


if __name__ == "__main__":
    typer.run(FiveDiversityConstraint().start)
