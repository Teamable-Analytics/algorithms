import os
from typing import Dict

import math

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
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.average_project_requirements_coverage import AverageProjectRequirementsCoverage
from benchmarking.evaluations.metrics.average_solo_status import AverageSoloStatus
from benchmarking.evaluations.metrics.envy_free_up_to_one_item import EnvyFreenessUpToOneItem
from benchmarking.evaluations.metrics.proportionality_up_to_one_item import ProportionalityUpToOneItem
from benchmarking.evaluations.scenarios.satisfy_project_requirements_and_diversify_female_min_of_2_and_diversify_african_min_of_2 import \
    SatisfyProjectRequirementsAndDiversifyFemaleMinOf2AndDiversifyAfricanMinOf2
from benchmarking.runs.external_algorithms.custom_dataclasses import ExternalAlgorithmScenarioAttribute, \
    ExternalAlgorithmDevelopmentSkill, ExternalAlgorithmYearCoding, ExternalAlgorithmInitialTeamProvider
from benchmarking.runs.external_algorithms.utils import calculate_students_utilities, calculate_student_utility
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class SatisfyProjectRequirementAndDiversifyFemaleMin2AndDiversifyAfricanMin2(Run):
    def start(self, num_trials: int = 1, generate_graphs: bool = False):
        CLASS_SIZES = [20, 100, 200, 300, 400, 500]
        MAX_TEAM_SIZE = 5

        ratio_of_female_students = 0.4
        ratio_of_african_students = 0.4

        # Graphs
        graph_runtime_dict = {}
        graph_ef1_dict = {}
        graph_prop1_dict = {}
        graph_avg_solo_status_dict = {}
        graph_project_requirement_coverage_dict = {}

        graph_dicts = [
            graph_runtime_dict,
            graph_ef1_dict,
            graph_prop1_dict,
            graph_avg_solo_status_dict,
            graph_project_requirement_coverage_dict,
        ]

        artifacts: Dict[int, SimulationSetArtifact] = {}

        for class_size in CLASS_SIZES:
            print("CLASS SIZE /", class_size)

            number_of_teams = math.ceil(class_size / MAX_TEAM_SIZE)
            metrics: Dict[str, TeamSetMetric] = {
                "EnvyFreenessUpToOneItem": EnvyFreenessUpToOneItem(
                    calculate_utilities=calculate_students_utilities,
                ),
                "ProportionalityUpToOneItem": ProportionalityUpToOneItem(
                    calculate_utilities=calculate_students_utilities,
                ),
                "AverageSoloStatus": AverageSoloStatus(),
                "AverageProjectRequirementsCoverage": AverageProjectRequirementsCoverage(),
            }

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
                            (Gpa.A, 0.2),
                            (Gpa.B, 0.2),
                            (Gpa.C, 0.2),
                            (Gpa.D, 0.2),
                            (Gpa.F, 0.2),
                        ],
                        ExternalAlgorithmScenarioAttribute.NUMBER_OF_YEARS_CODING.value: [
                            (ExternalAlgorithmYearCoding.LESS_THAN_ONE_YEAR, 0.25),
                            (ExternalAlgorithmYearCoding.ONE_YEAR, 0.25),
                            (ExternalAlgorithmYearCoding.TWO_YEAR, 0.25),
                            (ExternalAlgorithmYearCoding.MORE_THAN_TWO_YEARS, 0.25),
                        ],
                        ExternalAlgorithmScenarioAttribute.GIT_SKILL.value: [
                            (ExternalAlgorithmDevelopmentSkill.NO_SKILL, 0.25),
                            (ExternalAlgorithmDevelopmentSkill.BASIC_SKILL, 0.25),
                            (ExternalAlgorithmDevelopmentSkill.INTERMEDIATE_SKILL, 0.25),
                            (ExternalAlgorithmDevelopmentSkill.ADVANCED_SKILL, 0.25),
                        ],
                        ExternalAlgorithmScenarioAttribute.FE_DEVELOPMENT_SKILL.value: [
                            (ExternalAlgorithmDevelopmentSkill.NO_SKILL, 0.25),
                            (ExternalAlgorithmDevelopmentSkill.BASIC_SKILL, 0.25),
                            (ExternalAlgorithmDevelopmentSkill.INTERMEDIATE_SKILL, 0.25),
                            (ExternalAlgorithmDevelopmentSkill.ADVANCED_SKILL, 0.25),
                        ],
                        ExternalAlgorithmScenarioAttribute.BE_DEVELOPMENT_SKILL.value: [
                            (ExternalAlgorithmDevelopmentSkill.NO_SKILL, 0.25),
                            (ExternalAlgorithmDevelopmentSkill.BASIC_SKILL, 0.25),
                            (ExternalAlgorithmDevelopmentSkill.INTERMEDIATE_SKILL, 0.25),
                            (ExternalAlgorithmDevelopmentSkill.ADVANCED_SKILL, 0.25),
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
                            MAX_KEEP=15,
                            MAX_SPREAD=30,
                            MAX_ITERATE=30,
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
                                    "../../../..",
                                    "api/ai/external_algorithms/group_matcher_algorithm/group-matcher/run.py",
                                )
                            ),
                        ),
                    ],
                },
            ).run(num_runs=num_trials)

            artifacts[class_size] = simulation_set_artifact


if __name__ == "__main__":
    SatisfyProjectRequirementAndDiversifyFemaleMin2AndDiversifyAfricanMin2().start()
