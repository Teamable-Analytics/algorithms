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
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
    Gender,
)
from api.models.tokenization_constraint import TokenizationConstraint
from benchmarking.evaluations.enums import PreferenceDirection, PreferenceSubject
from benchmarking.evaluations.goals import PreferenceGoal, WeightGoal, DiversityGoal
from benchmarking.evaluations.graphing.graph_3d import graph_3d, Surface3D
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineSimilarity
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.metrics.utils.team_calculations import (
    is_happy_team_1hp_friend,
    is_strictly_happy_team_friend,
)
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.larger_simple_runs.custom_student_providers import (
    Major,
    Custom120SocialAndDiversityStudentProvider,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class SocialAndDiversity(Run):
    CLASS_SIZE = 120
    NUMBER_OF_TEAMS = 30
    NUMBER_OF_STUDENTS_PER_TEAM = 4

    def start(self, num_trials: int = 30, generate_graphs: bool = True):
        # Ranges
        max_keep_range = [1] + list(range(5, 31, 5))
        max_spread_range = [1] + list(range(5, 31, 5)) + [100]
        max_iterations_range = [1, 5, 10, 20, 30] + [250]

        scenario = SocialAndDiversityScenario(
            max_num_friends=1,
            max_num_enemies=0,
            value_of_female=Gender.FEMALE.value,
            value_of_math=Major.MATH.value,
            value_of_21=21,
        )

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
            "AverageSocialSatisfaction": AverageSocialSatisfaction(
                metric_function=is_strictly_happy_team_friend
            ),
            "AverageCosineSimilarity": AverageCosineSimilarity(),
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
                    student_provider=Custom120SocialAndDiversityStudentProvider(),
                    cache_key=f"priority_algorithm/larger_simple_runs/class_size_120/social_and_diversity/",
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
                    graph_3d(
                        surfaces,
                        graph_title=f"Priority Algorithm Parameters vs {metric_name}\n~Social & Diversity Scenario, {max_iterations} iterations, 120 students~",
                        x_label="MAX_KEEP",
                        y_label="MAX_SPREAD",
                        z_label=metric_name,
                        z_lim=(0, 1),
                        invert_xaxis=True,
                        plot_legend=True,
                    )


class SocialAndDiversityScenario(Scenario):
    def __init__(
        self,
        max_num_friends: int,
        max_num_enemies: int,
        value_of_female: int,
        value_of_math: int,
        value_of_21: int,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.max_num_friends = max_num_friends
        self.max_num_enemies = max_num_enemies
        self.value_of_female = value_of_female
        self.value_of_math = value_of_math
        self.value_of_21 = value_of_21

    @property
    def name(self):
        return (
            "Create teams that group social friends together then diversifies students"
        )

    @property
    def goals(self) -> List[Goal]:
        return [
            PreferenceGoal(
                PreferenceDirection.INCLUDE,
                PreferenceSubject.FRIENDS,
                max_num_friends=self.max_num_friends,
                max_num_enemies=self.max_num_enemies,
            ),
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
                ScenarioAttribute.AGE.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_21,
                ),
            ),
            WeightGoal(diversity_goal_weight=1, social_preference_weight=2),
        ]


if __name__ == "__main__":
    typer.run(SocialAndDiversity().start)
