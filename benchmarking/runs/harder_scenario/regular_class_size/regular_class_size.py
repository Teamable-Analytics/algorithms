import itertools
import random
import re
from typing import Dict, Tuple

import numpy as np
import typer
from matplotlib import pyplot as plt, cm

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig, WeightAlgorithmConfig
from api.models.enums import ScenarioAttribute, RequirementOperator, Gpa, AlgorithmType
from api.models.project import Project, ProjectRequirement
from benchmarking.caching.utils import SimulationArtifact
from benchmarking.data.simulated_data.mock_initial_teams_provider import MockInitialTeamsProvider, \
    MockInitialTeamsProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProviderSettings, MockStudentProvider
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.satisfy_project_requirements import SatisfyProjectRequirements
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class RegularClassSize(Run):
    CLASS_SIZE = 120
    NUMBER_OF_STUDENTS_PER_TEAM = 4
    NUMBER_OF_TEAMS = CLASS_SIZE // NUMBER_OF_STUDENTS_PER_TEAM
    NUMBER_OF_PROJECTS = 3
    CACHE_KEY = "priority_algorithm/harder_scenario/regular_class_size/regular_class_size/"
    MAX_SPREAD_RANGES = [3, 5, 10, 20, 50, 100]
    MAX_KEEP_RANGES = [3, 5, 10, 20, 50, 100]
    MAX_ITERATIONS_RANGES = [750, 1000, 1500, 2000]

    def run(self, num_trials: int = 30, generate_graphs: bool = False):
        scenario = SatisfyProjectRequirements()

        all_projects = [
            Project(
                _id=-1,
                name="Project 1",
                requirements=[
                    ProjectRequirement(
                        attribute=ScenarioAttribute.GPA.value,
                        operator=RequirementOperator.EXACTLY,
                        value=Gpa.A.value,
                    ),
                ],
            ),
            Project(
                _id=-2,
                name="Project 2",
                requirements=[
                    ProjectRequirement(
                        attribute=ScenarioAttribute.GPA.value,
                        operator=RequirementOperator.EXACTLY,
                        value=Gpa.B.value,
                    ),
                ],
            ),
            Project(
                _id=-3,
                name="Project 3",
                requirements=[
                    ProjectRequirement(
                        attribute=ScenarioAttribute.GPA.value,
                        operator=RequirementOperator.EXACTLY,
                        value=Gpa.C.value,
                    )
                ],
            )
        ]

        random.shuffle(all_projects)
        projects = []
        for idx, proj in enumerate(itertools.cycle(all_projects)):
            projects.append(Project(
                _id=idx,
                name=f'{proj.name} - {idx}',
                requirements=proj.requirements,
            ))

            if len(projects) == self.NUMBER_OF_TEAMS:
                break


        initial_teams_provider = MockInitialTeamsProvider(
            settings=MockInitialTeamsProviderSettings(
                projects=projects,
            )
        )

        student_provider_settings = MockStudentProviderSettings(
            number_of_students=self.CLASS_SIZE,
            attribute_ranges={
                ScenarioAttribute.GPA.value: [
                    (Gpa.A, 0.083333333333333333),   # 10/120
                    (Gpa.C, 0.083333333333333333),   # 10/120
                    (Gpa.D, 0.83333333333333333),   # 100/120
                ],
            },
        )

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
        }

        artifact: SimulationSetArtifact = SimulationSet(
            settings=SimulationSettings(
                scenario=scenario,
                student_provider=MockStudentProvider(student_provider_settings),
                cache_key=self.CACHE_KEY,
                initial_teams_provider=initial_teams_provider,
            ),
            algorithm_set={
                AlgorithmType.WEIGHT: [WeightAlgorithmConfig()],
                AlgorithmType.PRIORITY: [
                    PriorityAlgorithmConfig()
                ] + [
                    PriorityAlgorithmConfig(
                        MAX_SPREAD=max_spread,
                        MAX_KEEP=max_keep,
                        MAX_ITERATE=max_iterate,
                        MAX_TIME=10000000,
                        name=f'priority-max_spread_{max_spread}-max_keep_{max_keep}-max_iterate_{max_iterate}'
                    ) for max_spread, max_keep, max_iterate in itertools.product(
                        self.MAX_SPREAD_RANGES,
                        self.MAX_KEEP_RANGES,
                        self.MAX_ITERATIONS_RANGES,
                    )
                ],
            },
        ).run(num_runs=num_trials)

        artifacts_dict: Dict[
            Tuple[int, int, int], SimulationArtifact
        ] = {}
        for name, simulation_artifact in artifact.items():
            match = re.search(
                r"max_spread_(\d+)-max_keep_(\d+)-max_iterate_(\d+)", name
            )
            if match:
                max_keep = int(match.group(1))
                max_spread = int(match.group(2))
                max_iterations = int(match.group(3))
                artifacts_dict[(max_keep, max_spread, max_iterations)] = simulation_artifact

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
                for max_iterations in self.MAX_ITERATIONS_RANGES:
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
                        f"Priority Algorithm Parameters vs Priorities Satisfied\n~{max_iterations} iterations~"
                    )
                    ax.set_xlabel("MAX_KEEP")
                    ax.set_ylabel("MAX_SPREAD")
                    ax.set_zlabel("Score")
                    ax.set_zlim(np.min(Z), np.max(Z))
                    plt.show()


if __name__ == "__main__":
    typer.run(RegularClassSize().start)
