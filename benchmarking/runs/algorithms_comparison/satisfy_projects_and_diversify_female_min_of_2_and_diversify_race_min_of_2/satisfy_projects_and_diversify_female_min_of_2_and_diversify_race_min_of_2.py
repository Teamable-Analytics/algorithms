import os
from typing import Dict

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    RandomAlgorithmConfig,
    DoubleRoundRobinAlgorithmConfig,
    WeightAlgorithmConfig,
    GroupMatcherAlgorithmConfig,
)
from api.dataclasses.enums import (
    Gender,
    Race,
    RequirementOperator,
    ScenarioAttribute,
    AlgorithmType,
)
from api.dataclasses.project import Project, ProjectRequirement
from api.dataclasses.student import Student
from api.dataclasses.team import TeamShell
from benchmarking.data.simulated_data.realistic_class.providers import (
    RealisticMockInitialTeamsProvider,
    RealisticMockStudentProvider,
    TECHNICAL_SKILLS,
    DevelopmentSkills,
    WORK_EXPERIENCE,
    WorkExperience,
    GITHUB_EXPERIENCE,
    GithubExperience,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.metrics.average_project_requirements_coverage import (
    AverageProjectRequirementsCoverage,
)
from benchmarking.evaluations.metrics.average_solo_status import AverageSoloStatus
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.satisfy_project_requirements_and_diversify_female_min_of_2_and_diversify_african_min_of_2 import (
    SatisfyProjectRequirementsAndDiversifyFemaleMinOf2AndDiversifyAfricanMinOf2,
)
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import InsightOutput, Insight
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings


def additive_utility_function(student: Student, team: TeamShell) -> float:
    if len(team.requirements) == 0:
        return 0.0

    return sum(
        [student.meets_requirement(requirement) for requirement in team.requirements]
    ) / float(len(team.requirements))


class SatisfyProjectsAndDiversifyFemaleMinOf2AndDiversifyRaceMinOf2Run(Run):
    @staticmethod
    def better_algorithm_name(algorithm_name: str) -> str:
        algorithm_name_dict = {
            "AlgorithmType.DRR-default": "Double Round Robin",
            "AlgorithmType.WEIGHT-default": "Weight",
            "AlgorithmType.PRIORITY-default": "Priority",
            "AlgorithmType.RANDOM-default": "Random",
            "AlgorithmType.GROUP_MATCHER-default": "Group Matcher",
            "AlgorithmType.PRIORITY-SmallerParam": "Priority (smaller parameters)",
        }

        return algorithm_name_dict.get(algorithm_name, algorithm_name)

    @staticmethod
    def better_metric_name(metric_name: str) -> str:
        metric_name_dict = {
            "PrioritySatisfaction": "Priority Satisfaction",
            "AverageProjectRequirementsCoverage": "Average Project Coverage",
            "AverageCosineDifference": "Average Intra-Heterogeneity",
            "AverageSoloStatus": "Average Solo Status",
            "AverageSoloStatusGender": "Average Solo Status Gender",
        }

        return metric_name_dict.get(metric_name, metric_name)

    def start(
        self, num_trials: int = 1, generate_graphs: bool = False, analysis: bool = False
    ):
        scenario = (
            SatisfyProjectRequirementsAndDiversifyFemaleMinOf2AndDiversifyAfricanMinOf2(
                value_of_female=Gender.FEMALE.value,
                value_of_african=Race.African.value,
            )
        )

        initial_projects = [
            Project(
                _id=1,
                name="Face blur video sending and receiving using Amazon Web Services (AWS)",
                requirements=[
                    ProjectRequirement(
                        attribute=TECHNICAL_SKILLS,
                        operator=RequirementOperator.EXACTLY,
                        value=DevelopmentSkills.AWS.value,
                    ),
                    ProjectRequirement(
                        attribute=TECHNICAL_SKILLS,
                        operator=RequirementOperator.EXACTLY,
                        value=DevelopmentSkills.Frontend.value,
                    ),
                    ProjectRequirement(
                        attribute=TECHNICAL_SKILLS,
                        operator=RequirementOperator.EXACTLY,
                        value=DevelopmentSkills.Backend.value,
                    ),
                    ProjectRequirement(
                        attribute=WORK_EXPERIENCE,
                        operator=RequirementOperator.MORE_THAN,
                        value=WorkExperience.Two_Semesters.value,
                    ),
                    ProjectRequirement(
                        attribute=GITHUB_EXPERIENCE,
                        operator=RequirementOperator.MORE_THAN,
                        value=GithubExperience.Beginner.value,
                    ),
                ],
            ),
            Project(
                _id=2,
                name="Left over food delivery mobile app",
                requirements=[
                    ProjectRequirement(
                        attribute=WORK_EXPERIENCE,
                        operator=RequirementOperator.LESS_THAN,
                        value=WorkExperience.Two_Semesters.value,
                    ),
                    ProjectRequirement(
                        attribute=TECHNICAL_SKILLS,
                        operator=RequirementOperator.EXACTLY,
                        value=DevelopmentSkills.Mobile.value,
                    ),
                    ProjectRequirement(
                        attribute=TECHNICAL_SKILLS,
                        operator=RequirementOperator.EXACTLY,
                        value=DevelopmentSkills.ReactNative.value,
                    ),
                ],
            ),
            Project(
                _id=3,
                name="Collaborative website to play games with each other using PyGame",
                requirements=[
                    ProjectRequirement(
                        attribute=TECHNICAL_SKILLS,
                        operator=RequirementOperator.EXACTLY,
                        value=DevelopmentSkills.Python.value,
                    ),
                    ProjectRequirement(
                        attribute=TECHNICAL_SKILLS,
                        operator=RequirementOperator.EXACTLY,
                        value=DevelopmentSkills.Frontend.value,
                    ),
                    ProjectRequirement(
                        attribute=TECHNICAL_SKILLS,
                        operator=RequirementOperator.EXACTLY,
                        value=DevelopmentSkills.Design.value,
                    ),
                    ProjectRequirement(
                        attribute=GITHUB_EXPERIENCE,
                        operator=RequirementOperator.EXACTLY,
                        value=GithubExperience.Advanced.value,
                    ),
                ],
            ),
            Project(
                _id=4,
                name="Create an Internal Website for Scheduling for a Company",
                requirements=[
                    ProjectRequirement(
                        attribute=WORK_EXPERIENCE,
                        operator=RequirementOperator.LESS_THAN,
                        value=WorkExperience.Two_Semesters.value,
                    ),
                    ProjectRequirement(
                        attribute=TECHNICAL_SKILLS,
                        operator=RequirementOperator.EXACTLY,
                        value=DevelopmentSkills.Backend.value,
                    ),
                    ProjectRequirement(
                        attribute=TECHNICAL_SKILLS,
                        operator=RequirementOperator.EXACTLY,
                        value=DevelopmentSkills.Next.value,
                    ),
                ],
            ),
            Project(
                _id=5,
                name="Dating app for pets",
                requirements=[
                    ProjectRequirement(
                        attribute=TECHNICAL_SKILLS,
                        operator=RequirementOperator.EXACTLY,
                        value=DevelopmentSkills.Mobile.value,
                    ),
                    ProjectRequirement(
                        attribute=TECHNICAL_SKILLS,
                        operator=RequirementOperator.EXACTLY,
                        value=DevelopmentSkills.Backend.value,
                    ),
                    ProjectRequirement(
                        attribute=TECHNICAL_SKILLS,
                        operator=RequirementOperator.EXACTLY,
                        value=DevelopmentSkills.Frontend.value,
                    ),
                    ProjectRequirement(
                        attribute=TECHNICAL_SKILLS,
                        operator=RequirementOperator.EXACTLY,
                        value=DevelopmentSkills.Django.value,
                    ),
                ],
            ),
        ]

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
                name="Priority Satisfaction",
            ),
            "AverageProjectRequirementsCoverage": AverageProjectRequirementsCoverage(),
            "AverageCosineDifference": AverageCosineDifference(
                attribute_filter=[
                    ScenarioAttribute.GENDER.value,
                    ScenarioAttribute.RACE.value,
                ],
            ),
            "AverageSoloStatus": AverageSoloStatus(
                minority_groups_map={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            # Cosine
            # Solo status
        }

        class_sizes = [20, 100, 240, 500, 1000]
        team_size = 4

        simulation_sets: Dict[int, SimulationSetArtifact] = {}

        for class_size in class_sizes:
            print("CLASS SIZE /", class_size)
            cache_key = f"algorithms_comparison/sanity_check/single_run/class_size_{class_size}"

            initial_team_provider = RealisticMockInitialTeamsProvider(
                num_teams=class_size // team_size
            )

            student_provider = RealisticMockStudentProvider(class_size)
            simulation_settings = SimulationSettings(
                scenario=scenario,
                student_provider=student_provider,
                initial_teams_provider=initial_team_provider,
                cache_key=cache_key,
            )

            deterministic_artifacts = SimulationSet(
                settings=simulation_settings,
                algorithm_set={
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_TIME=10000000,
                            MAX_KEEP=30,
                            MAX_SPREAD=100,
                            MAX_ITERATE=250,
                            name="LargerParams",
                        ),
                    ],
                },
            ).run(num_runs=num_trials)

            deterministic_artifacts.update(
                SimulationSet(
                    settings=simulation_settings,
                    algorithm_set={
                        AlgorithmType.PRIORITY: [
                            PriorityAlgorithmConfig(
                                MAX_TIME=10000000,
                                MAX_KEEP=15,
                                MAX_SPREAD=30,
                                MAX_ITERATE=30,
                                name="SmallerParam",
                            ),
                        ],
                    },
                ).run(num_runs=num_trials)
            )

            simulation_sets[class_size] = deterministic_artifacts

        if generate_graphs:
            graph_data: Dict[str, Dict[str, GraphData]] = {}

            for class_size in class_sizes:
                artifact: SimulationSetArtifact = simulation_sets[class_size]
                insight_set: Dict[str, InsightOutput] = Insight.get_output_set(
                    artifact=artifact, metrics=list(metrics.values())
                )

                average_metrics: Dict[str, Dict[str, float]] = {}
                for metric_name in [Insight.KEY_RUNTIMES, *metrics.keys()]:
                    if metric_name == Insight.KEY_RUNTIMES:
                        average_metrics[metric_name] = Insight.average_metric(
                            insight_set, metric_name
                        )
                    else:
                        average_metrics[metric_name] = Insight.average_metric(
                            insight_set, metrics[metric_name].name
                        )

                for metric_name, average_metric in average_metrics.items():
                    if metric_name not in graph_data:
                        graph_data[metric_name] = {}
                    for algorithm_name, value in average_metric.items():
                        new_algorithm_name = self.better_algorithm_name(algorithm_name)
                        if new_algorithm_name not in graph_data[metric_name]:
                            graph_data[metric_name][new_algorithm_name] = GraphData(
                                x_data=[class_size],
                                y_data=[value],
                                name=new_algorithm_name,
                            )
                        else:
                            graph_data[metric_name][new_algorithm_name].x_data.append(
                                class_size
                            )
                            graph_data[metric_name][new_algorithm_name].y_data.append(
                                value
                            )

            for metric_name in [Insight.KEY_RUNTIMES, *list(metrics.keys())]:
                y_label = (
                    "Run time (seconds)"
                    if metric_name == Insight.KEY_RUNTIMES
                    else self.better_metric_name(metrics[metric_name].name)
                )
                y_lim = (
                    None
                    if metric_name == Insight.KEY_RUNTIMES
                    else GraphAxisRange(0, 1)
                )
                line_graph(
                    LineGraphMetadata(
                        x_label="Class Size",
                        y_label=y_label,
                        title=f"Mock Data Scenario: Satisfy Project Requirements,\nand Diversify Females and Africans with Min 2\n~ {y_label} vs Class Size",
                        data=list(graph_data[metric_name].values()),
                        y_lim=y_lim,
                    ),
                )

        if analysis:
            for algorithm_name in [
                "AlgorithmType.DRR-default",
                "AlgorithmType.GROUP_MATCHER-default",
            ]:
                max_max_team_size = []
                min_min_team_size = []
                average_average_team_size = []

                for class_size in class_sizes:
                    artifact: SimulationSetArtifact = simulation_sets[class_size]

                    teamsets = artifact[algorithm_name][0]
                    max_num_team = -1
                    min_num_team = 100000
                    average_team_generated = 0
                    max_team_sizes = []
                    min_team_sizes = []
                    average_team_sizes_in_teamset = []

                    for teamset in teamsets:
                        max_num_team = max(max_num_team, teamset.num_teams)
                        min_num_team = min(min_num_team, teamset.num_teams)
                        average_team_generated += teamset.num_teams

                        max_team_size = -1
                        min_team_size = 100000
                        average_team_size_in_teamset = 0

                        for team in teamset.teams:
                            max_team_size = max(max_team_size, team.size)
                            min_team_size = min(min_team_size, team.size)
                            average_team_size_in_teamset += team.size

                        max_team_sizes.append(max_team_size)
                        max_max_team_size.append(max_team_size)
                        min_team_sizes.append(min_team_size)
                        min_min_team_size.append(min_team_size)
                        average_team_sizes_in_teamset.append(
                            float(average_team_size_in_teamset)
                            / float(teamset.num_teams)
                        )
                        average_average_team_size.append(
                            float(average_team_size_in_teamset)
                            / float(teamset.num_teams)
                        )

                    average_team_generated /= float(len(teamsets))

                    print(f"Class size: {class_size}, Algorithm: {algorithm_name}")
                    print(
                        f"Max num team: {max_num_team}, Min num team: {min_num_team}, Average num team: {average_team_generated}"
                    )
                    print(
                        f"Max team sizes: {max(max_team_sizes)}, Min team sizes: {min(min_team_sizes)}, Average team sizes: {sum(average_team_sizes_in_teamset) / float(len(average_team_sizes_in_teamset))}"
                    )
                    print()

                print(f"Summary for Algorithm {algorithm_name}")
                print(
                    f"Max team sizes: {max(max_max_team_size)}, Min team sizes: {min(min_min_team_size)}, Average team sizes: {sum(average_average_team_size) / float(len(average_average_team_size))}"
                )
                print()
                print()


if __name__ == "__main__":
    typer.run(SatisfyProjectsAndDiversifyFemaleMinOf2AndDiversifyRaceMinOf2Run().start)
