import math
import os
from typing import Dict

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    WeightAlgorithmConfig,
    RandomAlgorithmConfig,
    GroupMatcherAlgorithmConfig,
)
from api.dataclasses.enums import ScenarioAttribute, Gender, AlgorithmType
from benchmarking.data.real_data.cosc341_w2021_t2_provider.providers import (
    COSC341W2021T2AnsweredSurveysStudentProvider,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.metrics.average_solo_status import AverageSoloStatus
from benchmarking.evaluations.metrics.average_timeslot_coverage import (
    AverageTimeslotCoverage,
)
from benchmarking.evaluations.metrics.cosine_similarity import (
    AverageCosineDifference,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.cosc341.concentrate_timeslot_diversify_gender_min_2_and_diversify_year_level import (
    ConcentrateTimeSlotDiversifyGenderMin2AndDiversifyYearLevel,
    DiversifyGenderMin2ConcentrateTimeSlotAndDiversifyYearLevel,
)
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import InsightOutput, Insight
from benchmarking.simulation.simulation_set import SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class Scenario1(Run):
    TEAM_SIZE = 4
    """
    This run focuses on the scenario of concentrating timeslots, diversifying females with min 2, and diversifying based 
    on year level (third year vs. graduate students).
    """

    def start(self, num_trials: int = 1, compute_metrics: bool = True):
        scenario_1 = ConcentrateTimeSlotDiversifyGenderMin2AndDiversifyYearLevel()
        scenario_2 = DiversifyGenderMin2ConcentrateTimeSlotAndDiversifyYearLevel()

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario_1.goals),
                False,
            ),
            "AverageTimeslotCoverage": AverageTimeslotCoverage(
                available_timeslots=[1, 2, 3, 4, 5, 6],
            ),
            "GenderCosineDifference": AverageCosineDifference(
                name="GenderCosineDifference",
                attribute_filter=[ScenarioAttribute.GENDER.value],
            ),
            "YearLevelCosineDifference": AverageCosineDifference(
                name="YearLevelCosineDifference",
                attribute_filter=[ScenarioAttribute.YEAR_LEVEL.value],
            ),
            "AverageSoloStatus": AverageSoloStatus(
                minority_groups_map={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                }
            ),
        }

        student_provider = COSC341W2021T2AnsweredSurveysStudentProvider()
        cache_key = "real_data/cosc_341/scenario1"
        simulation_settings_1 = SimulationSettings(
            num_teams=math.ceil(175 / self.TEAM_SIZE),
            student_provider=student_provider,
            scenario=scenario_1,
            cache_key=cache_key,
        )

        simulation_settings_2 = SimulationSettings(
            num_teams=math.ceil(175 / self.TEAM_SIZE),
            student_provider=student_provider,
            scenario=scenario_2,
            cache_key=cache_key,
        )

        artifacts = SimulationSet(
            settings=simulation_settings_1,
            algorithm_set={
                AlgorithmType.WEIGHT: [
                    WeightAlgorithmConfig(),
                ],
                AlgorithmType.GROUP_MATCHER: [
                    GroupMatcherAlgorithmConfig(
                        csv_output_path=os.path.abspath(
                            os.path.join(
                                os.path.dirname(__file__),
                                "../../../..",
                                f"api/ai/group_matcher_algorithm/group-matcher/inpData/{175}-generated.csv",
                            )
                        ),
                        group_matcher_run_path=os.path.abspath(
                            os.path.join(
                                os.path.dirname(__file__),
                                "../../../..",
                                "api/ai/group_matcher_algorithm/group-matcher/run.py",
                            )
                        ),
                    ),
                ],
            },
        ).run(num_runs=1)

        artifacts.update(
            SimulationSet(
                settings=simulation_settings_1,
                algorithm_set={
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_TIME=1000000,
                            MAX_KEEP=30,
                            MAX_SPREAD=100,
                            MAX_ITERATE=250,
                        ),
                    ],
                    AlgorithmType.RANDOM: [
                        RandomAlgorithmConfig(),
                    ],
                },
            ).run(num_runs=num_trials)
        )

        artifacts.update(
            SimulationSet(
                settings=simulation_settings_2,
                algorithm_set={
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_TIME=1000000,
                            MAX_KEEP=30,
                            MAX_SPREAD=100,
                            MAX_ITERATE=250,
                            name="Switched Order Priority",
                        ),
                    ],
                    AlgorithmType.RANDOM: [
                        RandomAlgorithmConfig(),
                    ],
                },
            ).run(num_runs=num_trials)
        )

        if compute_metrics:
            graph_data: Dict[str, Dict[str, GraphData]] = {}
            insight_set: Dict[str, InsightOutput] = Insight.get_output_set(
                artifact=artifacts, metrics=list(metrics.values())
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
                            x_data=[175],
                            y_data=[value],
                            name=algorithm_name,
                        )
                    else:
                        graph_data[metric_name][algorithm_name].x_data.append(175)
                        graph_data[metric_name][algorithm_name].y_data.append(value)

            # Print data as csv
            data = {
                "": list(graph_data["PrioritySatisfaction"].keys()),
            }
            for metric_name, inner_data in graph_data.items():
                data[metric_name] = []
                for algorithm_name, g_data in inner_data.items():
                    data[metric_name].extend([str(_) for _ in g_data.y_data])
            for k, v in data.items():
                print(",".join([k] + v))

            # Calculate Inter-Homogeneity from stdev of cosine difference
            print("GenderInterHomogeneity", end="")
            for algorithm_name, (team_sets, run_times) in artifacts.items():
                cosine_diffs = []
                for team_set in team_sets:
                    cosine_diffs.append(
                        AverageCosineDifference(
                            [ScenarioAttribute.GENDER.value]
                        ).calculate_stdev(team_set)
                    )
                print(f",{sum(cosine_diffs) / len(cosine_diffs)}", end="")
            print()

            # Calculate Inter-Homogeneity from stdev of cosine difference
            print("YearLevelInterHomogeneity", end="")
            for algorithm_name, (team_sets, run_times) in artifacts.items():
                cosine_diffs = []
                for team_set in team_sets:
                    cosine_diffs.append(
                        AverageCosineDifference(
                            [ScenarioAttribute.YEAR_LEVEL.value]
                        ).calculate_stdev(team_set)
                    )
                print(f",{sum(cosine_diffs) / len(cosine_diffs)}", end="")
            print()

            # Calculate Inter-Homogeneity from stdev of cosine difference
            print("TimeslotLevelInterHomogeneity", end="")
            for algorithm_name, (team_sets, run_times) in artifacts.items():
                cosine_diffs = []
                for team_set in team_sets:
                    cosine_diffs.append(
                        AverageCosineDifference(
                            [ScenarioAttribute.TIMESLOT_AVAILABILITY.value]
                        ).calculate_stdev(team_set)
                    )
                print(f",{sum(cosine_diffs) / len(cosine_diffs)}", end="")
            print()


if __name__ == "__main__":
    typer.run(Scenario1().start)
