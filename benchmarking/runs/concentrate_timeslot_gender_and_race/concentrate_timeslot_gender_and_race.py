import uuid
from pathlib import Path
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
from api.models.enums import AlgorithmType, ScenarioAttribute, Gender, Race
from api.models.student import Student
from api.models.team import TeamShell
from benchmarking.data.simulated_data.mock_initial_teams_provider import MockInitialTeamsProvider, \
    MockInitialTeamsProviderSettings
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.metrics.average_solo_status import AverageSoloStatus
from benchmarking.evaluations.metrics.average_timeslot_coverage import (
    AverageTimeslotCoverage,
)
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.concentrate_timeslot_and_concentrate_gender_and_concentrate_race import \
    ConcentrateTimeslotAndConcentrateGenderAndConcentrateRace
from benchmarking.runs.interfaces import Run
from benchmarking.evaluations.scenarios.concentrate_timeslot_and_diversify_gender_min_2_female import (
    ConcentrateTimeslotAndDiversifyGenderMin2Female,
)
from benchmarking.runs.timeslot_and_diversify_gender_min_2.custom_student_provider import (
    TimeslotCustomStudentProvider,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import InsightOutput, Insight
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact, _get_seeds
from benchmarking.simulation.simulation_settings import SimulationSettings


def additive_utility_function(student: Student, team: TeamShell) -> float:
    if len(team.requirements) == 0:
        return 0.0

    return sum(
        [student.meets_requirement(requirement) for requirement in team.requirements]
    ) / float(len(team.requirements))


class TimeSlotAndConcentrateGenderRace(Run):
    @staticmethod
    def better_algorithm_name(algorithm_name: str) -> str:
        algorithm_name_dict = {
            "AlgorithmType.DRR-default": "Double Round Robin",
            "AlgorithmType.WEIGHT-default": "Weight",
            "AlgorithmType.PRIORITY-default": "Priority",
            "AlgorithmType.RANDOM-default": "Random",
            "AlgorithmType.GROUP_MATCHER-default": "Group Matcher",
        }

        return algorithm_name_dict.get(algorithm_name, algorithm_name)

    @staticmethod
    def better_metric_name(metric_name: str) -> str:
        metric_name_dict = {
            "PrioritySatisfaction": "Priority Satisfaction",
            "AverageProjectRequirementsCoverage": "Average Project Requirements Coverage",
            "AverageCosineDifference": "Average Cosine Difference",
            "AverageSoloStatus": "Average Solo Status",
            "AverageSoloStatusGender": "Average Solo Status Gender"
        }

        return metric_name_dict.get(metric_name, metric_name)

    TEAM_SIZE = 4

    def start(self, num_trials: int = 30, generate_graphs: bool = False, cache_key_var: str = "concentrate_timeslots_gender_race"):
        scenario = ConcentrateTimeslotAndConcentrateGenderAndConcentrateRace(max_num_choices=5)

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
            cache_key = f"timeslot_stuff/{cache_key_var}/class_size_{class_size}"

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
                    # AlgorithmType.GROUP_MATCHER: [
                    #     GroupMatcherAlgorithmConfig(
                    #         csv_output_path=os.path.abspath(
                    #             os.path.join(
                    #                 os.path.dirname(__file__),
                    #                 "../../..",
                    #                 f"api/ai/group_matcher_algorithm/group-matcher/inpData/{class_size}-generated.csv"
                    #             )
                    #         ),
                    #         group_matcher_run_path=os.path.abspath(
                    #             os.path.join(
                    #                 os.path.dirname(__file__),
                    #                 "../../..",
                    #                 "api/ai/group_matcher_algorithm/group-matcher/run.py"
                    #             )
                    #         )
                    #     ),
                    # ]
                }
            ).run(num_runs=num_trials)

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

            for metric_name in metrics.keys():
                y_label = self.better_algorithm_name(metrics[metric_name].name)
                y_lim = GraphAxisRange(0, 1)
                line_graph(
                    LineGraphMetadata(
                        x_label="Class Size",
                        y_label=y_label,
                        title=f"Mock Data Scenario: Concentrate Timeslot Availability,\nand Concentrate Gender and Race\n~ {y_label} vs Class Size",
                        data=list(graph_data[metric_name].values()),
                        y_lim=y_lim,
                    ),
                )


if __name__ == "__main__":
    typer.run(TimeSlotAndConcentrateGenderRace().start)
