import itertools
import os
import numpy as np
import matplotlib.pyplot as plt
import re
from typing import Dict, List, Tuple

import typer
from matplotlib import cm
from api.ai.interfaces.algorithm_config import RandomAlgorithmConfig, WeightAlgorithmConfig, PriorityAlgorithmConfig, \
    GeneralizedEnvyGraphAlgorithmConfig, MultipleRoundRobinAlgorithmConfig, DoubleRoundRobinAlgorithmConfig
from api.ai.priority_algorithm.mutations import mutate_local_max, mutate_random_swap
from api.models.enums import ScenarioAttribute, RequirementOperator, Major, Gender, AlgorithmType
from api.models.project import Project, ProjectRequirement
from api.models.student import Student
from api.models.team import TeamShell
from benchmarking.caching.utils import SimulationArtifact
from benchmarking.data.simulated_data.mock_initial_teams_provider import MockInitialTeamsProvider, \
    MockInitialTeamsProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProviderSettings, MockStudentProvider
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.envy_free_up_to_one_item import EnvyFreenessUpToOneItem
from benchmarking.evaluations.metrics.envy_freeness import EnvyFreeness
from benchmarking.evaluations.metrics.num_requirements_satisfied import NumRequirementsSatisfied
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.metrics.proportionality import Proportionality
from benchmarking.evaluations.metrics.proportionality_up_to_one_item import ProportionalityUpToOneItem
from benchmarking.evaluations.scenarios.student_attributes_satisfy_project_requirements import \
    StudentAttributesSatisfyProjectRequirements
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


def get_students_utility(students: List[Student], team: TeamShell) -> float:
    if len(students) == 0:
        return 0.0

    return sum(
        [
            get_student_utility(student, team)
            for student in students
        ]
    ) / float(len(students))


def get_student_utility(student: Student, team: TeamShell) -> float:
    if len(team.requirements) == 0:
        return 1.0

    return sum(
        [
            1.0 if student.meets_requirement(requirement) else 0.0
            for requirement in team.requirements
        ]
    ) / float(len(team.requirements))


class StudentSatisfyProjectRequirements(Run):
    def start(self, num_trials: int = 10, generate_graphs: bool = True):
        NUM_PROJECTS = 5

        scenario = StudentAttributesSatisfyProjectRequirements()

        # Ranges
        max_keep_range = [5, 100, 250, 500, 750, 1000]
        max_spread_range = [1, 25, 50, 75, 100]
        max_iterations_range = [1500]

        completed_configs_dict = {
            "weight": [],
            # "random": [],
        }

        # files = []
        # for start_type in completed_configs_dict.keys():
        #     files.extend(os.listdir(
        #         os.path.join(
        #             os.path.dirname(__file__),
        #             "..",
        #             "..",
        #             "..",
        #             "..",
        #             "simulation_cache",
        #             f"student_attributes_satisfy_project_requirements_{start_type}_start",
        #
        #         )
        #     ))
        #
        # for file in files:
        #     if file.endswith(".json"):
        #         match = re.match(
        #             r"AlgorithmType.PRIORITY-max_keep_(\d+)-max_spread_(\d+)-max_iterations_(\d+)_(\w+)_start.json",
        #             file,
        #         )
        #         if match:
        #             max_keep = match.group(1)
        #             max_spread = match.group(2)
        #             max_iterations = match.group(3)
        #             start = match.group(4)
        #             completed_configs_dict[start].append(
        #                 (int(max_keep), int(max_spread), int(max_iterations))
        #             )

        class_size = 100
        team_size = 5
        num_teams = class_size // team_size

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
        }

        projects = [
            # This project needs third-year or more Computer Science students with a GPA of at least 80
            Project(
                _id=1,
                name="Project 1",
                number_of_teams=class_size // NUM_PROJECTS,
                requirements=[
                    ProjectRequirement(
                        attribute=ScenarioAttribute.GPA.value,
                        operator=RequirementOperator.MORE_THAN,
                        value=79,
                    ),
                    ProjectRequirement(
                        attribute=ScenarioAttribute.MAJOR.value,
                        operator=RequirementOperator.EXACTLY,
                        value=Major.Computer_Science.value,
                    ),
                    ProjectRequirement(
                        attribute=ScenarioAttribute.YEAR_LEVEL.value,
                        operator=RequirementOperator.MORE_THAN,
                        value=2,
                    )
                ]
            ),
            # This project needs Engineer students with a GPA of at least 50
            Project(
                _id=2,
                name="Project 2",
                number_of_teams=class_size // NUM_PROJECTS,
                requirements=[
                    ProjectRequirement(
                        attribute=ScenarioAttribute.GPA.value,
                        operator=RequirementOperator.MORE_THAN,
                        value=49,
                    ),
                    ProjectRequirement(
                        attribute=ScenarioAttribute.MAJOR.value,
                        operator=RequirementOperator.EXACTLY,
                        value=Major.Engineering.value,
                    )
                ]
            ),
            # This project needs 4th-year or more students
            Project(
                _id=3,
                name="Project 3",
                number_of_teams=class_size // NUM_PROJECTS,
                requirements=[
                    ProjectRequirement(
                        attribute=ScenarioAttribute.YEAR_LEVEL.value,
                        operator=RequirementOperator.MORE_THAN,
                        value=3,
                    )
                ]
            ),
            # This project needs female students from Science
            Project(
                _id=4,
                name="Project 4",
                number_of_teams=class_size // NUM_PROJECTS,
                requirements=[
                    ProjectRequirement(
                        attribute=ScenarioAttribute.GENDER.value,
                        operator=RequirementOperator.EXACTLY,
                        value=Gender.FEMALE.value,
                    ),
                    ProjectRequirement(
                        attribute=ScenarioAttribute.MAJOR.value,
                        operator=RequirementOperator.EXACTLY,
                        value=Major.Science.value,
                    )
                ]
            ),
            # This project accepts anyone
            Project(
                _id=5,
                name="Project 5",
                number_of_teams=class_size // NUM_PROJECTS,
                requirements=[]
            ),
        ]

        project_generator = itertools.cycle(projects)
        team_idx = 1
        initial_teams: List[TeamShell] = []
        while len(initial_teams) < num_teams:
            project = next(project_generator)
            initial_teams.append(
                TeamShell(
                    _id=team_idx,
                    name=f"Team {team_idx}",
                    project_id=project.id,
                    requirements=project.requirements,
                )
            )
            team_idx += 1

        student_provider_settings = MockStudentProviderSettings(
            number_of_students=class_size,
            attribute_ranges={
                ScenarioAttribute.GPA.value: [
                    (80, 0.2),
                    (60, 0.3),
                    (40, 0.5),
                ],
                ScenarioAttribute.MAJOR.value: [
                    (Major.Computer_Science.value, 0.2),
                    (Major.Engineering.value, 0.2),
                    (Major.Science.value, 0.2),
                    (Major.Other.value, 0.4),
                ],
                ScenarioAttribute.YEAR_LEVEL.value: [
                    (1, 0.24),
                    (2, 0.22),
                    (3, 0.22),
                    (4, 0.24),
                    (5, 0.08),
                ],
                ScenarioAttribute.GENDER.value: [
                    (Gender.MALE.value, 0.5),
                    (Gender.FEMALE.value, 0.5),
                ],
            },
        )

        artifacts_dict = {}
        for start_type, completed_configs in completed_configs_dict.items():
            algorithm_set = {
                AlgorithmType.PRIORITY: [
                    PriorityAlgorithmConfig(
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=max_spread,
                        MAX_ITERATE=max_iterations,
                        MAX_TIME=10000000,
                        name=f"max_keep_{max_keep}-max_spread_{max_spread}-max_iterations_{max_iterations}_{start_type}_start",
                    )
                    for max_keep in max_keep_range
                    for max_spread in max_spread_range
                    for max_iterations in max_iterations_range
                    # if (max_keep, max_spread, max_iterations) in completed_configs
                ],
            }

            artifact: SimulationSetArtifact = SimulationSet(
                settings=SimulationSettings(
                    scenario=scenario,
                    student_provider=MockStudentProvider(student_provider_settings),
                    cache_key=f"student_attributes_satisfy_project_requirements_{start_type}_start",
                    initial_teams_provider=MockInitialTeamsProvider(
                        MockInitialTeamsProviderSettings(
                            projects=projects,
                        )
                    )
                ),
                algorithm_set=algorithm_set,
            ).run(num_runs=num_trials)

            artifacts_dict[start_type]: Dict[
                Tuple[int, int, int], SimulationArtifact
            ] = {}
            for name, simulation_artifact in artifact.items():
                match = re.search(
                    r"max_keep_(\d+)-max_spread_(\d+)-max_iterations_(\d+)", name
                )
                if match:
                    max_keep = int(match.group(1))
                    max_spread = int(match.group(2))
                    max_iterations = int(match.group(3))
                    artifacts_dict[start_type][
                        (max_keep, max_spread, max_iterations)
                    ] = simulation_artifact

        # Run Weight algorithm for comparison
        weight_artifact: SimulationSetArtifact = SimulationSet(
            settings=SimulationSettings(
                num_teams=num_teams,
                scenario=scenario,
                student_provider=MockStudentProvider(student_provider_settings),
                cache_key=f"student_attributes_satisfy_project_requirements_default",
            ),
            algorithm_set={
                AlgorithmType.WEIGHT: [WeightAlgorithmConfig()],
                AlgorithmType.PRIORITY: [PriorityAlgorithmConfig()],
            },
        ).run(num_runs=num_trials)
        insight_output_set = Insight.get_output_set(
            weight_artifact, list(metrics.values())
        )
        avg_metric_output = Insight.average_metric(
            insight_output_set=insight_output_set, metric_name="PrioritySatisfaction"
        )
        avg_run_time = Insight.average_metric(
            insight_output_set=insight_output_set, metric_name=Insight.KEY_RUNTIMES
        )

        print("avg_metric_output:", avg_metric_output)
        print("avg_run_time:", avg_run_time)

        if generate_graphs:
            for metric_name, metric in metrics.items():
                points_dict = {}
                for start_type, artifacts in artifacts_dict.items():
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
                    points_dict[start_type] = points

                wireframe = True
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

                        ##### \/ \/ \/ \/ TEMP. REMOVE LATER \/ \/ \/ \/ #####
                        remove_missing_points = True
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
                        # print(X, Y, Z)
                        surface = (
                            ax.plot_wireframe(
                                X,
                                Y,
                                Z,
                                color=("blue" if start_type == "weight" else "red"),
                                label=f"{start_type} start".title(),
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
                    ax.legend()
                    ax.set_zlim(0, 1)
                    plt.show()




if __name__ == "__main__":
    typer.run(StudentSatisfyProjectRequirements().start)
