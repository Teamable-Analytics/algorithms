import os
from typing import Dict, List

import math
import typer

from api.ai.interfaces.algorithm_config import (
    RandomAlgorithmConfig,
    PriorityAlgorithmConfig,
    DoubleRoundRobinAlgorithmConfig,
    MultipleRoundRobinAlgorithmConfig,
    GeneralizedEnvyGraphAlgorithmConfig,
    GroupMatcherAlgorithmConfig
)
from api.dataclasses.enums import Gpa, ScenarioAttribute, Gender, Race, AlgorithmType
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProviderSettings, MockStudentProvider
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.average_project_requirements_coverage import AverageProjectRequirementsCoverage
from benchmarking.evaluations.metrics.average_solo_status import AverageSoloStatus
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.evaluations.metrics.envy_free_up_to_one_item import EnvyFreenessUpToOneItem
from benchmarking.evaluations.metrics.num_teams import NumberOfTeams
from benchmarking.evaluations.metrics.proportionality_up_to_one_item import ProportionalityUpToOneItem
from benchmarking.evaluations.scenarios.satisfy_project_requirements_and_diversify_female_min_of_2_and_diversify_african_min_of_2 import \
    SatisfyProjectRequirementsAndDiversifyFemaleMinOf2AndDiversifyAfricanMinOf2
from benchmarking.runs.external_algorithms.custom_dataclasses import ExternalAlgorithmScenarioAttribute, \
    ExternalAlgorithmDevelopmentSkill, ExternalAlgorithmYearCoding, ExternalAlgorithmInitialTeamProvider
from benchmarking.runs.external_algorithms.utils import calculate_students_utilities, calculate_student_utility
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class SatisfyProjectRequirementAndDiversifyFemaleMin2AndDiversifyAfricanMin2(Run):
    def start(self, num_trials: int = 1, generate_graphs: bool = False):
        CLASS_SIZES = [20, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        MAX_TEAM_SIZE = 5

        ratio_of_female_students = 0.2
        ratio_of_african_students = 0.2

        # Graphs
        graph_runtime_dict = {}
        graph_ef1_dict = {}
        graph_prop1_dict = {}
        graph_avg_solo_status_dict = {}
        graph_project_requirement_coverage_dict = {}
        graph_gender_cosine_difference_dict = {}
        graph_race_cosine_difference_dict = {}
        graph_num_teams_dict = {}

        graph_dicts = [
            graph_runtime_dict,
            graph_ef1_dict,
            graph_prop1_dict,
            graph_avg_solo_status_dict,
            graph_project_requirement_coverage_dict,
            graph_gender_cosine_difference_dict,
            graph_race_cosine_difference_dict,
            graph_num_teams_dict,
        ]

        artifacts: Dict[int, SimulationSetArtifact] = {}
        metrics: Dict[str, TeamSetMetric] = {
            "EnvyFreenessUpToOneItem": EnvyFreenessUpToOneItem(
                calculate_utilities=calculate_students_utilities,
            ),
            "ProportionalityUpToOneItem": ProportionalityUpToOneItem(
                calculate_utilities=calculate_students_utilities,
            ),
            "AverageSoloStatus": AverageSoloStatus(
                minority_groups_map={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            "AverageProjectRequirementsCoverage": AverageProjectRequirementsCoverage(),
            "GenderCosineDifference": AverageCosineDifference(
                name="GenderCosineDifference",
                attribute_filter=[ScenarioAttribute.GENDER.value],
            ),
            "RaceCosineDifference": AverageCosineDifference(
                name="RaceCosineDifference",
                attribute_filter=[ScenarioAttribute.RACE.value],
            ),
            "NumberOfTeams": NumberOfTeams(),
        }

        for class_size in CLASS_SIZES:
            print("CLASS SIZE /", class_size)

            number_of_teams = math.ceil(class_size / MAX_TEAM_SIZE)

            student_provider = MockStudentProvider(
                settings=MockStudentProviderSettings(
                    number_of_students=class_size,
                    attribute_ranges={
                        ScenarioAttribute.GENDER.value: [
                            (Gender.FEMALE, ratio_of_female_students),
                            (Gender.MALE, 1 - ratio_of_female_students),
                        ],
                        ScenarioAttribute.RACE.value: [
                            (Race.African, ratio_of_african_students),
                            (Race.European, 1 - ratio_of_african_students),
                        ],
                        ExternalAlgorithmScenarioAttribute.GPA.value: [
                            (Gpa.A, 0.1),
                            (Gpa.B, 0.4),
                            (Gpa.C, 0.2),
                            (Gpa.D, 0.2),
                            (Gpa.F, 0.1),
                        ],
                        ExternalAlgorithmScenarioAttribute.NUMBER_OF_YEARS_CODING.value: [
                            (ExternalAlgorithmYearCoding.LESS_THAN_ONE_YEAR, 0.2),
                            (ExternalAlgorithmYearCoding.ONE_YEAR, 0.5),
                            (ExternalAlgorithmYearCoding.TWO_YEAR, 0.2),
                            (ExternalAlgorithmYearCoding.MORE_THAN_TWO_YEARS, 0.1),
                        ],
                        ExternalAlgorithmScenarioAttribute.GIT_SKILL.value: [
                            (ExternalAlgorithmDevelopmentSkill.NO_SKILL, 0.2),
                            (ExternalAlgorithmDevelopmentSkill.BASIC_SKILL, 0.4),
                            (ExternalAlgorithmDevelopmentSkill.INTERMEDIATE_SKILL, 0.2),
                            (ExternalAlgorithmDevelopmentSkill.ADVANCED_SKILL, 0.2),
                        ],
                        ExternalAlgorithmScenarioAttribute.FE_DEVELOPMENT_SKILL.value: [
                            (ExternalAlgorithmDevelopmentSkill.NO_SKILL, 0.4),
                            (ExternalAlgorithmDevelopmentSkill.BASIC_SKILL, 0.3),
                            (ExternalAlgorithmDevelopmentSkill.INTERMEDIATE_SKILL, 0.2),
                            (ExternalAlgorithmDevelopmentSkill.ADVANCED_SKILL, 0.1),
                        ],
                        ExternalAlgorithmScenarioAttribute.BE_DEVELOPMENT_SKILL.value: [
                            (ExternalAlgorithmDevelopmentSkill.NO_SKILL, 0.4),
                            (ExternalAlgorithmDevelopmentSkill.BASIC_SKILL, 0.3),
                            (ExternalAlgorithmDevelopmentSkill.INTERMEDIATE_SKILL, 0.2),
                            (ExternalAlgorithmDevelopmentSkill.ADVANCED_SKILL, 0.1),
                        ],
                        ExternalAlgorithmScenarioAttribute.COMMUNICATION_SKILL.value: [
                            (ExternalAlgorithmDevelopmentSkill.NO_SKILL, 0.25),
                            (ExternalAlgorithmDevelopmentSkill.BASIC_SKILL, 0.25),
                            (ExternalAlgorithmDevelopmentSkill.INTERMEDIATE_SKILL, 0.25),
                            (ExternalAlgorithmDevelopmentSkill.ADVANCED_SKILL, 0.25),
                        ],
                    },
                )
            )

            simulation_set_artifact = SimulationSet(
                settings=SimulationSettings(
                    scenario=SatisfyProjectRequirementsAndDiversifyFemaleMinOf2AndDiversifyAfricanMinOf2(),
                    student_provider=student_provider,
                    initial_teams_provider=ExternalAlgorithmInitialTeamProvider(num_teams=number_of_teams),
                    cache_key=f"external_algorithms/satisfy_project_requirement_and_diversify_female_min_2_and_diversify_african_min_2_{number_of_teams}",
                ),
                algorithm_set={
                    AlgorithmType.RANDOM: [RandomAlgorithmConfig()],
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_KEEP=30,
                            MAX_SPREAD=100,
                            MAX_ITERATE=250,
                            MAX_TIME=10000000,
                        ),
                    ],
                    AlgorithmType.DRR: [
                        DoubleRoundRobinAlgorithmConfig(
                            utility_function=calculate_student_utility,
                        )
                    ],
                    AlgorithmType.MRR: [
                        MultipleRoundRobinAlgorithmConfig(
                            utility_function=calculate_student_utility,
                        )
                    ],
                    AlgorithmType.GEG: [
                        GeneralizedEnvyGraphAlgorithmConfig(
                            utility_function=calculate_student_utility,
                        ),
                    ],
                    AlgorithmType.GROUP_MATCHER: [
                        GroupMatcherAlgorithmConfig(
                            csv_output_path=os.path.abspath(
                                os.path.join(
                                    os.path.dirname(__file__),
                                    "../../..",
                                    f"api/ai/external_algorithms/group_matcher_algorithm/group-matcher/inpData/{class_size}-generated.csv",
                                )
                            ),
                            group_matcher_run_path=os.path.abspath(
                                os.path.join(
                                    os.path.dirname(__file__),
                                    "../../..",
                                    "api/ai/external_algorithms/group_matcher_algorithm/group-matcher/run.py",
                                )
                            ),
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
                ef1 = Insight.average_metric(
                    insight_set, "EnvyFreenessUpToOneItem"
                )
                prop1 = Insight.average_metric(
                    insight_set, "ProportionalityUpToOneItem"
                )
                avg_solo_status = Insight.average_metric(
                    insight_set, "AverageSoloStatus"
                )
                project_requirement_coverage = Insight.average_metric(
                    insight_set, "AverageProjectRequirementsCoverage"
                )
                gender_cosine_difference = Insight.average_metric(
                    insight_set, "GenderCosineDifference"
                )
                race_cosine_difference = Insight.average_metric(
                    insight_set, "RaceCosineDifference"
                )
                average_runtimes = Insight.average_metric(
                    insight_set, Insight.KEY_RUNTIMES
                )
                num_teams = Insight.average_metric(
                    insight_set, "NumberOfTeams"
                )
                metric_values = [average_runtimes, ef1, prop1, avg_solo_status, project_requirement_coverage, gender_cosine_difference, race_cosine_difference, num_teams]


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
                    y_label="Envy-freeness up to one item",
                    title="EF1",
                    data=list(graph_ef1_dict.values()),
                    y_lim=GraphAxisRange(
                        *metrics["EnvyFreenessUpToOneItem"].theoretical_range
                    ),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Proportionality up to one item",
                    title="PROP1",
                    data=list(graph_prop1_dict.values()),
                    y_lim=GraphAxisRange(
                        *metrics["ProportionalityUpToOneItem"].theoretical_range
                    ),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Average solo status",
                    title="Average solo status",
                    data=list(graph_avg_solo_status_dict.values()),
                    y_lim=GraphAxisRange(
                        *metrics["AverageSoloStatus"].theoretical_range
                    ),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Average project requirements coverage",
                    title="Average project requirements coverage",
                    data=list(graph_project_requirement_coverage_dict.values()),
                    y_lim=GraphAxisRange(
                        *metrics["AverageProjectRequirementsCoverage"].theoretical_range
                    ),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Gender Inter-Homogeneity",
                    title="Gender Inter-Homogeneity",
                    data=list(graph_gender_cosine_difference_dict.values()),
                    y_lim=GraphAxisRange(start=0, end=1),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Race Inter-Homogeneity",
                    title="Race Inter-Homogeneity",
                    data=list(graph_race_cosine_difference_dict.values()),
                    y_lim=GraphAxisRange(start=0, end=1),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Number of teams",
                    title="Number of teams",
                    data=list(graph_num_teams_dict.values()),
                )
            )

            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Run time (seconds)",
                    title="Run time",
                    data=list(graph_runtime_dict.values()),
                )
            )

if __name__ == "__main__":
    typer.run(SatisfyProjectRequirementAndDiversifyFemaleMin2AndDiversifyAfricanMin2().start)
