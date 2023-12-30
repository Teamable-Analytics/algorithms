import itertools
import math
import os
import re
from typing import Dict, List

import typer

from api.ai.interfaces.algorithm_config import RandomAlgorithmConfig, WeightAlgorithmConfig, PriorityAlgorithmConfig, \
    GeneralizedEnvyGraphAlgorithmConfig, MultipleRoundRobinAlgorithmConfig, DoubleRoundRobinAlgorithmConfig
from api.ai.priority_algorithm.mutations import mutate_local_max, mutate_random_swap
from api.models.enums import ScenarioAttribute, RequirementOperator, Major, Gender, AlgorithmType
from api.models.project import Project, ProjectRequirement
from api.models.student import Student
from api.models.team import TeamShell
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
        class_sizes = list(range(50, 3001, 50))
        NUM_PROJECTS = 5
        STUDENTS_PER_TEAM = 5

        scenario = StudentAttributesSatisfyProjectRequirements()
        metrics: Dict[str, TeamSetMetric] = {
            "NumRequirementsSatisfied": NumRequirementsSatisfied(),
            "EnvyFreeness": EnvyFreeness(calculate_utilities=get_students_utility),
            "EnvyFreenessUpToOneItem": EnvyFreenessUpToOneItem(calculate_utilities=get_students_utility),
            "Proportionality": Proportionality(calculate_utilities=get_students_utility),
            "ProportionalityUpToOneItem": ProportionalityUpToOneItem(calculate_utilities=get_students_utility),
        }

        artifacts: Dict[int, SimulationSetArtifact] = {}

        # Ranges
        max_keep_range = [10, 500, 1000, 1500, 2000, 2500]
        max_spread_range = [1, 10, 20, 30, 40, 50]
        max_iterations_range = [10, 250, 500, 750, 1000]

        completed_configs_dict = {
            "weight": [],
            # "random": [],
        }

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
        #         "project_scenario",
        #     )
        # )
        # for file in files:
        #     if file.endswith(".json"):
        #         match = re.match(
        #             r"AlgorithmType.PRIORITY-project_scenario-max_keep_(\d+)-max_spread_(\d+)-max_iterations_(\d+)_(\w+)_start.json",
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

        for start_type, completed_configs in completed_configs_dict.items():
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
                ],
            }

            simulation_set_artifact = SimulationSet(
                settings=SimulationSettings(
                    scenario=scenario,
                    student_provider=MockStudentProvider(student_provider_settings),
                    cache_key=f"student_attributes_satisfy_project_requirements_{num_teams}_{start_type}_start",
                    initial_teams_provider=MockInitialTeamsProvider(
                        MockInitialTeamsProviderSettings(
                            projects=projects,
                        )
                    )
                ),
                algorithm_set=algorithm_set,
            ).run(num_runs=num_trials)
            artifacts[class_size] = simulation_set_artifact

        # if generate_graphs:
        #     for class_size, artifact in artifacts.items():
        #         insight_set: Dict[str, Dict[str, List[float]]] = Insight.get_output_set(
        #             artifact=artifact, metrics=list(metrics.values())
        #         )

                # Data processing for graph
                # for i, metric in enumerate(metric_values):
                #     for name, data in metric.items():
                #         if name not in graph_dicts[i]:
                #             graph_dicts[i][name] = GraphData(
                #                 x_data=[class_size],
                #                 y_data=[data],
                #                 name=name,
                #             )
                #         else:
                #             graph_dicts[i][name].x_data.append(class_size)
                #             graph_dicts[i][name].y_data.append(data)
                #
                # line_graph(
                #     LineGraphMetadata(
                #         x_label="Class size",
                #         y_label="Run time (seconds)",
                #         title="Student Satisfy Project Requirements Runtimes",
                #         data=list(graph_runtime_dict.values()),
                #     )
                # )
                #
                # line_graph(
                #     LineGraphMetadata(
                #         x_label="Class size",
                #         y_label="Satisfied Requirements",
                #         title="Student Satisfy Project Requirements Satisfied Requirements",
                #         data=list(graph_satisfied_requirements_dict.values()),
                #     )
                # )
                #
                # line_graph(
                #     LineGraphMetadata(
                #         x_label="Class size",
                #         y_label="Envy Freeness",
                #         title="Student Satisfy Project Requirements Envy Freeness",
                #         data=list(graph_envy_freeness_dict.values()),
                #     )
                # )
                #
                # line_graph(
                #     LineGraphMetadata(
                #         x_label="Class size",
                #         y_label="Envy Freeness Up To One Item",
                #         title="Student Satisfy Project Requirements Envy Freeness Up To One Item",
                #         data=list(graph_envy_freeness_up_to_one_item_dict.values()),
                #     )
                # )
                #
                # line_graph(
                #     LineGraphMetadata(
                #         x_label="Class size",
                #         y_label="Proportionality",
                #         title="Student Satisfy Project Requirements Proportionality",
                #         data=list(graph_proportionality_dict.values()),
                #     )
                # )
                #
                # line_graph(
                #     LineGraphMetadata(
                #         x_label="Class size",
                #         y_label="Proportionality Up To One Item",
                #         title="Student Satisfy Project Requirements Proportionality Up To One Item",
                #         data=list(graph_proportionality_up_to_one_item_dict.values()),
                #     )
                # )


if __name__ == "__main__":
    typer.run(StudentSatisfyProjectRequirements().start)
