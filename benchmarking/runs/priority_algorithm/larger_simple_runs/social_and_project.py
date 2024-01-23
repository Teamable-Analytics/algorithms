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
    RequirementsCriteria,
)
from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProvider,
    MockInitialTeamsProviderSettings,
)
from benchmarking.evaluations.enums import PreferenceDirection, PreferenceSubject
from benchmarking.evaluations.goals import (
    PreferenceGoal,
    WeightGoal,
    ProjectRequirementGoal,
)
from benchmarking.evaluations.graphing.graph_3d import graph_3d, Surface3D
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.metrics.average_project_requirements_coverage import (
    AverageProjectRequirementsCoverage,
)
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.metrics.utils.team_calculations import (
    is_happy_team_1hp_friend,
    is_strictly_happy_team_friend,
)
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.larger_simple_runs.custom_projects import (
    get_custom_projects,
)
from benchmarking.runs.priority_algorithm.larger_simple_runs.custom_student_providers import (
    Custom120SocialAndProjectsStudentProvider,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class SocialAndProject(Run):
    CLASS_SIZE = 120
    NUMBER_OF_TEAMS = 30
    NUMBER_OF_STUDENTS_PER_TEAM = 4

    def start(self, num_trials: int = 30, generate_graphs: bool = False):
        # Ranges
        max_keep_range = [1] + list(range(5, 31, 5))
        max_spread_range = [1] + list(range(20, 101, 20))
        max_iterations_range = [1] + list(range(50, 251, 50))

        scenario = SocialAndProjectScenario(
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
            "AverageProjectRequirementCoverage": AverageProjectRequirementsCoverage(),
        }
        initial_teams_provider = MockInitialTeamsProvider(
            settings=MockInitialTeamsProviderSettings(
                projects=get_custom_projects(),
            )
        )

        start_types = [
            PriorityAlgorithmStartType.WEIGHT,
            PriorityAlgorithmStartType.RANDOM,
        ]

        artifacts_dict = {start_type: {} for start_type in start_types}
        for start_type in start_types:
            artifact: SimulationSetArtifact = SimulationSet(
                settings=SimulationSettings(
                    scenario=scenario,
                    student_provider=Custom120SocialAndProjectsStudentProvider(),
                    initial_teams_provider=initial_teams_provider,
                    cache_key=f"priority_algorithm/larger_simple_runs/class_size_120/social_and_project/",
                ),
                algorithm_set={
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_KEEP=max_keep,
                            MAX_SPREAD=max_spread,
                            MAX_ITERATE=max_iterations,
                            MAX_TIME=10000000,
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
                        graph_title=f"Priority Algorithm Parameters vs {metric_name.title()}\n~Social & Projects Scenario, {max_iterations} iterations, 120 students~",
                        x_label="MAX_KEEP",
                        y_label="MAX_SPREAD",
                        z_label=metric_name,
                        z_lim=(0, 1),
                        invert_xaxis=True,
                        plot_legend=True,
                    )


class SocialAndProjectScenario(Scenario):
    def __init__(self, max_num_friends: int, max_num_enemies: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_num_friends = max_num_friends
        self.max_num_enemies = max_num_enemies

    @property
    def name(self):
        return "Create teams that group social friends together after satisfying project requirements"

    @property
    def goals(self) -> List[Goal]:
        return [
            ProjectRequirementGoal(
                criteria=RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED
            ),
            PreferenceGoal(
                PreferenceDirection.INCLUDE,
                PreferenceSubject.FRIENDS,
                max_num_friends=self.max_num_friends,
                max_num_enemies=self.max_num_enemies,
            ),
            WeightGoal(project_requirement_weight=2, social_preference_weight=1),
        ]


if __name__ == "__main__":
    typer.run(SocialAndProject().start)
