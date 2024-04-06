from typing import Dict
import os

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    WeightAlgorithmConfig,
    DoubleRoundRobinAlgorithmConfig,
    GroupMatcherAlgorithmConfig,
    RandomAlgorithmConfig,
)
from api.dataclasses.enums import ScenarioAttribute, Race, Gender, AlgorithmType
from api.dataclasses.student import Student
from api.dataclasses.team import TeamShell
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.metrics.average_solo_status import AverageSoloStatus
from benchmarking.evaluations.metrics.average_timeslot_coverage import (
    AverageTimeslotCoverage,
)
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.evaluations.scenarios.concentrate_timeslot_diversify_gender_min_2 import \
    ConcentrateTimeslotAndDiversifyGenderMin2Female
from benchmarking.runs.concentrate_timeslots.custom_dataclasses import TimeslotCustomStudentProvider
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.insight import InsightOutput, Insight
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings


def additive_utility_function(student: Student, team: TeamShell) -> float:
    if len(team.requirements) == 0:
        return 0.0

    return sum(
        [student.meets_requirement(requirement) for requirement in team.requirements]
    ) / float(len(team.requirements))


class TimeSlotAndDiversifyGenderMin2(Run):
    @staticmethod
    def better_algorithm_name(algorithm_name: str) -> str:
        algorithm_name_dict = {
            "AlgorithmType.DRR-default": "Double Round Robin",
            "AlgorithmType.WEIGHT-default": "Weight (Diversify)",
            "AlgorithmType.PRIORITY-default": "Priority (Diversify)",
            "AlgorithmType.RANDOM-default": "Random",
            "AlgorithmType.GROUP_MATCHER-default": "Group Matcher",
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
            "AverageTimeslotCoverage": "Average Common Time Availability",
        }

        return metric_name_dict.get(metric_name, metric_name)

    TEAM_SIZE = 4

    def start(self, num_trials: int = 100, generate_graphs: bool = True, analyze: bool = False):
        scenario = ConcentrateTimeslotAndDiversifyGenderMin2Female(max_num_choices=5)

        metrics = {
            # "PrioritySatisfaction": PrioritySatisfaction(
            #     goals_to_priorities(scenario.goals),
            #     False,
            # ),
            "AverageTimeslotCoverage": AverageTimeslotCoverage(
                available_timeslots=list(range(10)),
            ),
            "AverageCosineDifference": AverageCosineDifference(
                attribute_filter=[ScenarioAttribute.GENDER.value, ScenarioAttribute.RACE.value],
            ),
            "AverageSoloStatus": AverageSoloStatus(
                minority_groups={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
        }
        simulation_sets = {}

        class_sizes = [20, 100, 240, 500, 1000]
        # class_sizes = [20, 40, 60, 80, 100]

        for class_size in class_sizes:
            print("CLASS SIZE /", class_size)
            student_provider = TimeslotCustomStudentProvider(class_size)
            cache_key = f"timeslot_stuff/class_size_{class_size}"

            simulation_settings = SimulationSettings(
                num_teams=class_size // self.TEAM_SIZE,
                student_provider=student_provider,
                scenario=scenario,
                cache_key=cache_key,
            )

            simulation_sets[class_size] = SimulationSet(
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
                    AlgorithmType.GROUP_MATCHER: [
                        GroupMatcherAlgorithmConfig(
                            csv_output_path=os.path.abspath(
                                os.path.join(
                                    os.path.dirname(__file__),
                                    "../../..",
                                    f"api/ai/group_matcher_algorithm/group-matcher/inpData/{class_size}-generated.csv"
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
                    ]
                }
            ).run(num_runs=num_trials)

        if analyze:
            for algorithm_name in ['AlgorithmType.DRR-default', 'AlgorithmType.GROUP_MATCHER-default']:

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
                            float(average_team_size_in_teamset) / float(teamset.num_teams))
                        average_average_team_size.append(float(average_team_size_in_teamset) / float(teamset.num_teams))

                    average_team_generated /= float(len(teamsets))

                    print(f"Class size: {class_size}, Algorithm: {algorithm_name}")
                    print(
                        f"Max num team: {max_num_team}, Min num team: {min_num_team}, Average num team: {average_team_generated}")
                    print(
                        f"Max team sizes: {max(max_team_sizes)}, Min team sizes: {min(min_team_sizes)}, Average team sizes: {sum(average_team_sizes_in_teamset) / float(len(average_team_sizes_in_teamset))}")
                    print()

                print(f"Summary for Algorithm {algorithm_name}")
                print(
                    f"Max team sizes: {max(max_max_team_size)}, Min team sizes: {min(min_min_team_size)}, Average team sizes: {sum(average_average_team_size) / float(len(average_average_team_size))}")
                print()
                print()

        if generate_graphs:
            graph_data: Dict[str, Dict[str, GraphData]] = {}

            for class_size in class_sizes:
                artifact: SimulationSetArtifact = simulation_sets[class_size]
                insight_set: Dict[str, InsightOutput] = Insight.get_output_set(
                    artifact=artifact, metrics=list(metrics.values())
                )

                average_metrics: Dict[str, Dict[str, float]] = {}
                for metric_name in metrics.keys():
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
                            graph_data[metric_name][new_algorithm_name].y_data.append(value)

            for metric_name in metrics.keys():
                y_label = self.better_metric_name(metrics[metric_name].name)
                y_lim = GraphAxisRange(0, 1)
                line_graph(
                    LineGraphMetadata(
                        x_label="Class Size",
                        y_label=y_label,
                        title=f"Mock Data Scenario: Concentrate Timeslot Availability,\nand Diversify Females and Africans with Min 2\n~ {y_label} vs Class Size",
                        data=list(graph_data[metric_name].values()),
                        y_lim=y_lim,
                    ),
                )


if __name__ == "__main__":
    typer.run(TimeSlotAndDiversifyGenderMin2().start)
