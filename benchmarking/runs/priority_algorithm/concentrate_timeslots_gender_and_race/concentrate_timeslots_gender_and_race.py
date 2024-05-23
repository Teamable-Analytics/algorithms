from typing import Dict
import os
import pandas as pd

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    WeightAlgorithmConfig,
    DoubleRoundRobinAlgorithmConfig,
    GroupMatcherAlgorithmConfig,
    RandomAlgorithmConfig,
)
from api.dataclasses.enums import ScenarioAttribute, Gender, Race, AlgorithmType
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
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.concentrate_timeslots_and_concentrate_gender_and_concentrate_race import (
    ConcentrateTimeslotsAndConcentrateGenderAndConcentrateRace,
)
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.concentrate_timeslots_gender_and_race.custom_student_provider import (
    TimeslotCustomStudentProvider,
)
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


class ConcentrateTimeslotsAndConcentrateGenderAndConcentrateRaceRun(Run):
    @staticmethod
    def better_algorithm_name(algorithm_name: str) -> str:
        algorithm_name_dict = {
            "AlgorithmType.DRR-default": "Double Round Robin",
            "AlgorithmType.WEIGHT-default": "Weight (Concentrate)",
            "AlgorithmType.PRIORITY-default": "Priority (Concentrate)",
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

    def start(
        self,
        num_trials: int = 100,
        generate_graphs: bool = True,
        analytics: bool = False,
    ):
        scenario = ConcentrateTimeslotsAndConcentrateGenderAndConcentrateRace(
            max_num_choices=5
        )

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
            "AverageTimeslotCoverage": AverageTimeslotCoverage(
                available_timeslots=list(range(10)),
            ),
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
        }
        simulation_sets = {}

        class_sizes = [20, 100, 240, 500, 1000]

        for class_size in class_sizes:
            print("CLASS SIZE /", class_size)
            student_provider = TimeslotCustomStudentProvider(class_size)

            simulation_settings_1 = SimulationSettings(
                num_teams=class_size // self.TEAM_SIZE,
                student_provider=student_provider,
                scenario=scenario,
                cache_key=f"timeslot_runs/concentrate_timeslots_gender_race/part_1/class_size_{class_size}",
            )

            simulation_settings_2 = SimulationSettings(
                num_teams=class_size // self.TEAM_SIZE,
                student_provider=student_provider,
                scenario=scenario,
                cache_key=f"timeslot_runs/concentrate_timeslots_gender_race/part_2/class_size_{class_size}",
            )

            simulation_settings_3 = SimulationSettings(
                num_teams=class_size // self.TEAM_SIZE,
                student_provider=student_provider,
                scenario=scenario,
                cache_key=f"timeslot_runs/concentrate_timeslots_gender_race/part_3/class_size_{class_size}",
            )

            algorithm_set = {
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
                                f"api/ai/group_matcher_algorithm/group-matcher/inpData/{class_size}-generated.csv",
                            )
                        ),
                        group_matcher_run_path=os.path.abspath(
                            os.path.join(
                                os.path.dirname(__file__),
                                "../../..",
                                "api/ai/group_matcher_algorithm/group-matcher/run.py",
                            )
                        ),
                    ),
                ],
            }

            simulation_sets[class_size] = SimulationSet(
                settings=simulation_settings_1,
                algorithm_set=algorithm_set,
            ).run(num_runs=30)

            simulation_sets[class_size].update(
                SimulationSet(
                    settings=simulation_settings_2,
                    algorithm_set=algorithm_set,
                ).run(num_runs=35)
            )

            simulation_sets[class_size].update(
                SimulationSet(
                    settings=simulation_settings_3,
                    algorithm_set=algorithm_set,
                ).run(num_runs=35)
            )

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
                            graph_data[metric_name][new_algorithm_name].y_data.append(
                                value
                            )

            for metric_name in metrics.keys():
                y_label = self.better_metric_name(metrics[metric_name].name)
                y_lim = GraphAxisRange(0, 1)
                line_graph(
                    LineGraphMetadata(
                        x_label="Class Size",
                        y_label=y_label,
                        # title=f"Mock Data Scenario: Concentrate Timeslot Availability,\nand Concentrate Gender and Race\n~ {y_label} vs Class Size",
                        data=list(graph_data[metric_name].values()),
                        title=None,
                        y_lim=y_lim,
                    ),
                )

        # Analytics
        if analytics:
            analytics_map: Dict[int, Dict[str, Dict[str, float]]] = {}
            for class_size in class_sizes:
                analytics_map[class_size] = {}
                artifact: SimulationSetArtifact = simulation_sets[class_size]
                insight_set: Dict[str, InsightOutput] = Insight.get_output_set(
                    artifact=artifact, metrics=list(metrics.values())
                )

                # We only care about solo status
                metric = "AverageSoloStatus"
                avg = Insight.average_metric(insight_set, metrics[metric].name)
                stdev = Insight.metric_stdev(insight_set, metrics[metric].name)
                _min = Insight.metric_min(insight_set, metrics[metric].name)
                _max = Insight.metric_max(insight_set, metrics[metric].name)

                for algorithm_name in avg.keys():
                    analytics_map[class_size][
                        self.better_algorithm_name(algorithm_name)
                    ] = {
                        "Average": avg[algorithm_name],
                        "Standard Deviation": stdev[algorithm_name],
                        "Minimum": _min[algorithm_name],
                        "Maximum": _max[algorithm_name],
                    }

            # Make a multi-header table with 1st header as Algorithm name, 2nd header is the avg, stdev, min, max in pandas
            columns = pd.MultiIndex(
                levels=[
                    analytics_map[class_sizes[0]].keys(),
                    ["Average", "Standard Deviation", "Minimum", "Maximum"],
                ],
                codes=[[0, 0, 0, 0, 1, 1, 1, 1], [0, 1, 2, 3, 0, 1, 2, 3]],
            )
            df = pd.DataFrame(index=list(analytics_map.keys()), columns=columns)
            # Fill the table
            for class_size in class_sizes:
                for algorithm_name in analytics_map[class_size].keys():
                    for metric_name in analytics_map[class_size][algorithm_name].keys():
                        df.loc[
                            class_size, (algorithm_name, metric_name)
                        ] = analytics_map[class_size][algorithm_name][metric_name]

            # Print the table to
            df.to_(
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "concentrate_timeslots_gender_and_race.csv",
                    )
                )
            )


if __name__ == "__main__":
    typer.run(ConcentrateTimeslotsAndConcentrateGenderAndConcentrateRaceRun().start)
