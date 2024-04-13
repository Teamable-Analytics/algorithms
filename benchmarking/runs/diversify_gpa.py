import math
from typing import Dict, List

import typer

from api.ai.interfaces.algorithm_config import (
    RandomAlgorithmConfig,
    MultipleRoundRobinAlgorithmConfig,
)
from api.dataclasses.project import Project, ProjectRequirement
from api.dataclasses.student import Student
from api.dataclasses.team import TeamShell
from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProvider,
    MockInitialTeamsProviderSettings,
)
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.envy_free_up_to_one_item import (
    EnvyFreenessUpToOneItem,
)
from api.dataclasses.enums import (
    ScenarioAttribute,
    Gpa,
    AlgorithmType,
    RequirementOperator,
    Gender,
)
from benchmarking.evaluations.metrics.proportionality_up_to_one_item import (
    ProportionalityUpToOneItem,
)
from benchmarking.evaluations.scenarios.diversify_gpa import DiversifyGPA
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings


def mrr_utility_function(student: Student, team: TeamShell) -> float:
    return team.num_requirements_met_by_student(student) / len(team.requirements)


def utility_function(students: List[Student], team: TeamShell) -> float:
    entire_team_student = Student(
        _id=-team.id,
        attributes={},
    )
    for student in students:
        for attribute, value in student.attributes.items():
            if attribute not in entire_team_student.attributes:
                entire_team_student.attributes[attribute] = []
            entire_team_student.attributes[attribute].extend(value)

    return team.num_requirements_met_by_student(entire_team_student) / len(
        team.requirements
    )


class DiversifyGpaRun(Run):
    def start(self, num_trials: int = 10, generate_graphs: bool = True):
        """
        Goal: Run concentrate GPA scenario, and measure the average, maximum, and minimum gini scores for gpa
        """

        # Define changing values
        class_sizes = list(range(50, 501, 50))
        ratio_of_a_students = 0.3
        ratio_of_b_students = 0.5
        ratio_of_c_students = 0.2

        # Graph variables
        graph_runtime_dict = {}
        ef1_dict = {}
        prop1_dict = {}
        graph_dicts = [
            graph_runtime_dict,
            ef1_dict,
            prop1_dict,
        ]

        metrics: Dict[str, TeamSetMetric] = {
            "EnvyFreenessUpToOneItem": EnvyFreenessUpToOneItem(
                calculate_utilities=utility_function
            ),
            "ProportionalityUpToOneItem": ProportionalityUpToOneItem(
                calculate_utilities=utility_function
            ),
        }

        artifacts: Dict[int, SimulationSetArtifact] = {}

        for class_size in class_sizes:
            print("CLASS SIZE /", class_size)

            number_of_teams = math.ceil(class_size / 5)

            student_provider_settings = MockStudentProviderSettings(
                number_of_students=class_size,
                attribute_ranges={
                    ScenarioAttribute.GPA.value: [
                        (Gpa.A, ratio_of_a_students),
                        (Gpa.B, ratio_of_b_students),
                        (Gpa.C, ratio_of_c_students),
                    ],
                    ScenarioAttribute.GENDER.value: [
                        (Gender.FEMALE, 0.2),
                        (Gender.MALE, 0.8),
                    ],
                },
            )

            initial_teams_provider = MockInitialTeamsProvider(
                settings=MockInitialTeamsProviderSettings(
                    projects=[
                        Project(
                            _id=1,
                            name="Wants A students",
                            number_of_teams=number_of_teams,
                            requirements=[
                                ProjectRequirement(
                                    attribute=ScenarioAttribute.GPA.value,
                                    operator=RequirementOperator.EXACTLY,
                                    value=Gpa.A.value,
                                ),
                                ProjectRequirement(
                                    attribute=ScenarioAttribute.GENDER.value,
                                    operator=RequirementOperator.EXACTLY,
                                    value=Gender.FEMALE.value,
                                ),
                            ],
                        ),
                    ],
                )
            )

            simulation_set_artifact = SimulationSet(
                settings=SimulationSettings(
                    # num_teams=number_of_teams,
                    scenario=DiversifyGPA(),
                    student_provider=MockStudentProvider(student_provider_settings),
                    cache_key=f"concentrate_gpa_{number_of_teams}",
                    initial_teams_provider=initial_teams_provider,
                ),
                algorithm_set={
                    AlgorithmType.RANDOM: [RandomAlgorithmConfig()],
                    AlgorithmType.MRR: [
                        MultipleRoundRobinAlgorithmConfig(
                            utility_function=mrr_utility_function,
                            use_new_version=True,
                            name="NEW MRR",
                        ),
                        MultipleRoundRobinAlgorithmConfig(
                            utility_function=mrr_utility_function,
                            use_new_version=False,
                            name="Old MRR",
                        ),
                    ],
                },
            ).run(num_runs=num_trials)
            artifacts[class_size] = simulation_set_artifact

        if generate_graphs:
            for class_size, artifact in artifacts.items():
                insight_set: Dict[str, Dict[str, List[float]]] = Insight.get_output_set(
                    artifact=artifact, metrics=list(metrics.values())
                )

                ef1 = Insight.average_metric(insight_set, "EnvyFreenessUpToOneItem")
                prop1 = Insight.average_metric(
                    insight_set, "ProportionalityUpToOneItem"
                )
                average_runtimes = Insight.average_metric(
                    insight_set, Insight.KEY_RUNTIMES
                )
                metric_values = [
                    average_runtimes,
                    ef1,
                    prop1,
                ]
                # Data processing for graph
                for i, metric in enumerate(metric_values):
                    for name, data in metric.items():
                        if name not in graph_dicts[i]:
                            graph_dicts[i][name] = GraphData(
                                x_data=[class_size],
                                y_data=[data],
                                name=name,
                            )
                        else:
                            graph_dicts[i][name].x_data.append(class_size)
                            graph_dicts[i][name].y_data.append(data)

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Run time (seconds)",
                    title="Diversify GPA Runtimes",
                    data=list(graph_runtime_dict.values()),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Envy Free Up To One Item",
                    title="Diversify GPA Envy Free Up To One Item",
                    data=list(ef1_dict.values()),
                    y_lim=GraphAxisRange(start=0, end=1.01),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Proportionality Up To One Item",
                    title="Diversify GPA Proportionality Up To One Item",
                    data=list(prop1_dict.values()),
                    y_lim=GraphAxisRange(start=0, end=1.01),
                )
            )


if __name__ == "__main__":
    typer.run(DiversifyGpaRun().start)
