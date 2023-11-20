import math
from typing import Dict, List

import typer

from api.ai.interfaces.algorithm_config import DoubleRoundRobinAlgorithmConfig, \
    MultipleRoundRobinAlgorithmConfig, GeneralizedEnvyGraphAlgorithmConfig
from api.models.enums import ScenarioAttribute, Gender, AlgorithmType, RequirementOperator
from api.models.project import Project, ProjectRequirement
from api.models.student import Student
from api.models.team import TeamShell
from benchmarking.data.simulated_data.mock_initial_teams_provider import MockInitialTeamsProviderSettings, \
    MockInitialTeamsProvider
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.envy_free_up_to_one_item import EnvyFreenessUpToOneItem
from benchmarking.evaluations.metrics.envy_freeness import EnvyFreeness
from benchmarking.evaluations.metrics.proportionality import Proportionality
from benchmarking.evaluations.metrics.proportionality_up_to_one_item import ProportionalityUpToOneItem
from benchmarking.evaluations.scenarios.diversify_gender_min_2_female import (
    DiversifyGenderMin2Female,
)
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings


class DiversifyGenderMin2AsProjectRequirementRun(Run):
    @staticmethod
    def start(num_trials: int = 10, generate_graphs: bool = True):
        """
        Goal: Run diversify gender scenario, measure average EF, EF1, PROP, and PROP1
        """

        # Defining our changing x-values (in the graph sense)
        class_sizes = list(range(50, 101, 50))
        ratio_of_female_students = 0.2

        graph_runtime_dict = {}
        graph_avg_ef_dict = {}
        graph_avg_ef1_dict = {}
        graph_avg_prop_dict = {}
        graph_avg_prop1_dict = {}
        graph_dicts = [
            graph_runtime_dict,
            graph_avg_ef_dict,
            graph_avg_ef1_dict,
            graph_avg_prop_dict,
            graph_avg_prop1_dict,
        ]

        metrics: Dict[str, TeamSetMetric] = {
            "EF": EnvyFreeness(
                calculate_utilities=DiversifyGenderMin2AsProjectRequirementRun.get_team_utility,
            ),
            "EF1": EnvyFreenessUpToOneItem(
                calculate_utilities=DiversifyGenderMin2AsProjectRequirementRun.get_team_utility,
            ),
            "PROP": Proportionality(
                calculate_utilities=DiversifyGenderMin2AsProjectRequirementRun.get_team_utility,
            ),
            "PROP1": ProportionalityUpToOneItem(
                calculate_utilities=DiversifyGenderMin2AsProjectRequirementRun.get_team_utility,
            ),
        }

        artifacts: Dict[int, SimulationSetArtifact] = {}

        for class_size in class_sizes:
            print("CLASS SIZE /", class_size)

            number_of_teams = math.ceil(class_size / 5)

            # set up either mock or real data
            student_provider_settings = MockStudentProviderSettings(
                number_of_students=class_size,
                attribute_ranges={
                    ScenarioAttribute.GENDER.value: [
                        (Gender.MALE, 1 - ratio_of_female_students),
                        (Gender.FEMALE, ratio_of_female_students),
                    ],
                },
            )

            # All teams should have num_female >= 2
            projects: List[Project] = [
                Project(
                    _id=i,
                    name=f"Project {i}",
                    requirements=[
                        ProjectRequirement(
                            attribute=ScenarioAttribute.GENDER.value,
                            operator=RequirementOperator.MORE_THAN,
                            value=1
                        ),
                        ProjectRequirement(
                            attribute=ScenarioAttribute.GENDER.value,
                            operator=RequirementOperator.EXACTLY,
                            value=2
                        )
                    ],
                )
                for i in range(1, number_of_teams + 1)
            ]

            scenario = DiversifyGenderMin2Female(value_of_female=Gender.FEMALE.value, projects=projects)

            initialTeamsProviderSettings = MockInitialTeamsProviderSettings(projects=projects)
            initialTeamsProvider = MockInitialTeamsProvider(settings=initialTeamsProviderSettings)

            simulation_set_artifact = SimulationSet(
                settings=SimulationSettings(
                    scenario=scenario,
                    student_provider=MockStudentProvider(student_provider_settings),
                    cache_key=f"diversify_gender_min_2_{number_of_teams}",
                    initial_teams_provider=initialTeamsProvider,
                ),
                algorithm_set={
                    AlgorithmType.DRR: [DoubleRoundRobinAlgorithmConfig(name='Double Round Robin')],
                    AlgorithmType.MRR: [MultipleRoundRobinAlgorithmConfig(name='Multiple Round Robin')],
                    AlgorithmType.GEG: [GeneralizedEnvyGraphAlgorithmConfig(name='Generalized Envy Graph')],
                },
            ).run(num_runs=num_trials)
            artifacts[class_size] = simulation_set_artifact

        if generate_graphs:
            for class_size, artifact in artifacts.items():
                insight_set: Dict[str, Dict[str, List[float]]] = Insight.get_output_set(
                    artifact=artifact, metrics=list(metrics.values())
                )

                average_ef = Insight.average_metric(insight_set, "EnvyFreeness")
                average_ef1 = Insight.average_metric(insight_set, "EnvyFreenessUpToOneItem")
                average_prop = Insight.average_metric(insight_set, "Proportionality")
                average_prop1 = Insight.average_metric(insight_set, "ProportionalityUpToOneItem")
                average_runtimes = Insight.average_metric(
                    insight_set, Insight.KEY_RUNTIMES
                )

                metric_values = [
                    average_runtimes,
                    average_ef,
                    average_ef1,
                    average_prop,
                    average_prop1,
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
                    title="Diversify Gender With Min of Two Runtimes",
                    data=list(graph_runtime_dict.values()),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="EF",
                    title="Diversify Gender With Min of Two Average EF",
                    data=list(graph_avg_ef_dict.values()),
                    y_lim=GraphAxisRange(start=-0.01, end=1.05),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="EF1",
                    title="Diversify Gender With Min of Two Average EF1",
                    data=list(graph_avg_ef1_dict.values()),
                    y_lim=GraphAxisRange(start=-0.01, end=1.05),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="PROP",
                    title="Diversify Gender With Min of Two Average PROP",
                    data=list(graph_avg_prop_dict.values()),
                    y_lim=GraphAxisRange(start=-0.01, end=1.05),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="PROP1",
                    title="Diversity Gender With Min of Two Average PROP1",
                    data=list(graph_avg_prop1_dict.values()),
                    y_lim=GraphAxisRange(start=-0.01, end=1.05),
                )
            )

    @staticmethod
    def get_team_utility(students: List[Student], team: TeamShell) -> float:
        return sum(
            [
                1.0 if student.meets_requirement(requirement) else -1.0
                for requirement in team.requirements
                for student in students
            ]
        )


if __name__ == "__main__":
    typer.run(DiversifyGenderMin2AsProjectRequirementRun.start)
