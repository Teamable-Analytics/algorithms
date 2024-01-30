import itertools
import os
import uuid
from typing import Dict

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    RandomAlgorithmConfig,
    DoubleRoundRobinAlgorithmConfig,
    WeightAlgorithmConfig,
    GroupMatcherAlgorithmConfig,
)
from api.models.enums import RequirementOperator, AlgorithmType, Gender, Race
from api.models.project import Project, ProjectRequirement
from api.models.student import Student
from api.models.team import TeamShell
from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProvider,
    MockInitialTeamsProviderSettings,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.metrics.average_project_requirements_coverage import (
    AverageProjectRequirementsCoverage,
)
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineSimilarity
from benchmarking.evaluations.metrics.envy_free_up_to_one_item import EnvyFreenessUpToOneItem
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.scenario_that_we_love import (
    ScenarioThatWeLove,
)
from benchmarking.runs.interfaces import Run
from benchmarking.runs.project_scenario_with_different_algos.student_provider import (
    TECHNICAL_SKILLS,
    DevelopmentSkills,
    GITHUB_EXPERIENCE,
    GithubExperience,
    WORK_EXPERIENCE,
    WorkExperience,
    CustomStudentProvider,
)
from benchmarking.runs.timeslot_and_diversify_gender_min_2.timeslot_and_diversify_gender_min_2 import TimeSlotAndDiversifyGenderMin2
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


class CustomModels(Run):
    def start(self, num_trials: int = 100, generate_graphs: bool = True):
        scenario = ScenarioThatWeLove(
            value_of_female=Gender.FEMALE.value,
            value_of_african=Race.African.value,
        )

        initial_projecys = [
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
            "AverageProjectRequirementsCoverage": AverageProjectRequirementsCoverage(
                name="Average Project Requirements Coverage"
            ),
            "AverageCosineSimilarity": AverageCosineSimilarity()
            # Cosine
            # Solo status
        }

        class_sizes = [20, 100, 240, 500, 1000]
        # class_sizes = [20, 40, 60, 80, 100]
        # class_sizes = [20]
        team_size = 4

        simulation_sets: Dict[int, SimulationSetArtifact] = {}

        for class_size in class_sizes:
            print("CLASS SIZE /", class_size)

            project_cycler = itertools.cycle(initial_projecys)
            projects = []

            for i in range(class_size // team_size):
                next_project = next(project_cycler)
                projects.append(
                    Project(
                        _id=i,
                        name=next_project.name + " " + str(i),
                        requirements=next_project.requirements,
                    )
                )

            initial_team_provider = MockInitialTeamsProvider(
                settings=MockInitialTeamsProviderSettings(projects=projects)
            )

            student_provider = CustomStudentProvider(class_size)
            simulation_settings = SimulationSettings(
                scenario=scenario,
                student_provider=student_provider,
                initial_teams_provider=initial_team_provider,
                cache_key=f"custom_models/class_size_{class_size}",
            )

            deterministic_artifacts = SimulationSet(
                settings=simulation_settings,
                algorithm_set={
                    AlgorithmType.DRR: [
                        DoubleRoundRobinAlgorithmConfig(
                            utility_function=additive_utility_function
                        ),
                    ],
                    AlgorithmType.WEIGHT: [
                        WeightAlgorithmConfig(),
                    ],
                    AlgorithmType.GROUP_MATCHER: [
                        GroupMatcherAlgorithmConfig(
                            csv_output_path=os.path.abspath(
                                os.path.join(
                                    os.path.dirname(__file__),
                                    "../../..",
                                    f"api/ai/group_matcher_algorithm/group-matcher/inpData/{class_size}-{uuid.uuid4()}-generated.csv"
                                )
                            ),
                            group_matcher_run_path=os.path.abspath(
                                os.path.join(
                                    os.path.dirname(__file__),
                                    "../../..",
                                    "api/ai/group_matcher_algorithm/group-matcher/run.py"
                                )
                            )
                        ),
                    ],
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_TIME=10000000,
                            MAX_KEEP=30,
                            MAX_SPREAD=100,
                            MAX_ITERATE=250,
                        ),
                    ],
                    AlgorithmType.RANDOM: [
                        RandomAlgorithmConfig(),
                    ],
                },
            ).run(num_runs=100)
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
                        if algorithm_name not in graph_data[metric_name]:
                            graph_data[metric_name][algorithm_name] = GraphData(
                                x_data=[class_size],
                                y_data=[value],
                                name=algorithm_name,
                            )
                        else:
                            graph_data[metric_name][algorithm_name].x_data.append(
                                class_size
                            )
                            graph_data[metric_name][algorithm_name].y_data.append(value)

            for metric_name in [Insight.KEY_RUNTIMES, *list(metrics.keys())]:
                y_label = (
                    "Run time (seconds)"
                    if metric_name == Insight.KEY_RUNTIMES
                    else metrics[metric_name].name
                )
                y_lim = (
                    None
                    if metric_name == Insight.KEY_RUNTIMES
                    else GraphAxisRange(0, 1.1)
                )
                line_graph(
                    LineGraphMetadata(
                        x_label="Class Size",
                        y_label=y_label,
                        title="Project - Diversity Scenarios",
                        data=list(graph_data[metric_name].values()),
                        y_lim=y_lim,
                    ),
                )


if __name__ == "__main__":
    typer.run(CustomModels().start)
    typer.run(TimeSlotAndDiversifyGenderMin2().start)
