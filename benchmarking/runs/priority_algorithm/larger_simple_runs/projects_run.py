import itertools
import random
import re

import numpy as np
import typer
from matplotlib import pyplot as plt

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    WeightAlgorithmConfig,
)
from api.models.enums import (
    ScenarioAttribute,
    RequirementOperator,
    AlgorithmType,
    AttributeValueEnum,
)
from api.models.project import Project, ProjectRequirement
from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProvider,
    MockInitialTeamsProviderSettings,
)
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProviderSettings,
    MockStudentProvider,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings

from typing import List, Dict, Tuple

from api.models.enums import RequirementsCriteria
from benchmarking.evaluations.goals import ProjectRequirementGoal
from benchmarking.evaluations.interfaces import Scenario, Goal


class Gpa(AttributeValueEnum):
    A = 1
    B = 2
    C = 3
    D = 4


class SatisfyProjectRequirements(Scenario):
    @property
    def name(self) -> str:
        return "Students Meet Project Requirements"

    @property
    def goals(self) -> List[Goal]:
        return [
            ProjectRequirementGoal(
                criteria=RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED
            ),
        ]


class RegularClassSize(Run):
    CLASS_SIZE = 120
    NUMBER_OF_TEAMS = 24
    NUMBER_OF_STUDENTS_PER_TEAM = 5
    NUMBER_OF_PROJECTS = 3
    CACHE_KEY = "priority_algorithm/larger_simple_runs/"

    def start(self, num_trials: int = 30, generate_graphs: bool = False):
        # Ranges
        max_keep_range = [1] + list(range(5, 31, 5))
        max_spread_range = [1] + list(range(5, 31, 5))
        max_iterations_range = [1, 5, 10, 20, 30]

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
            ),
        ]

        random.shuffle(all_projects)
        projects = []
        for idx, proj in enumerate(itertools.cycle(all_projects)):
            projects.append(
                Project(
                    _id=idx,
                    name=f"{proj.name} - {idx}",
                    requirements=proj.requirements,
                )
            )

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
                    (Gpa.A.value, float(1 / 15)),
                    (Gpa.B.value, float(1 / 15)),
                    (Gpa.C.value, float(1 / 15)),
                    (Gpa.D.value, float(12 / 15)),  # (☭ ͜ʖ ☭) nice
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
                cache_key=f"priority_algorithm/larger_simple_runs/class_size_120/projects_run/",
                initial_teams_provider=initial_teams_provider,
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
                    f"Priority Algorithm Parameters vs Priorities Satisfied\n~Five Diversity Constraint, {max_iterations} iterations, 120 students~"
                )
                ax.set_xlabel("MAX_KEEP")
                ax.set_ylabel("MAX_SPREAD")
                ax.set_zlabel("Score")
                ax.set_zlim(0, 1)
                plt.show()


if __name__ == "__main__":
    typer.run(RegularClassSize().start)
