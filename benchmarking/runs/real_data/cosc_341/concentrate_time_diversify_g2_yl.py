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
from benchmarking.evaluations.scenarios.cosc341.concentrate_timeslot_diversify_all_min_2_diversify_student_level import (
    ConcentrateTimeSlotDiversifyAllGenderMin2DiversifyYearLevel,
)
from benchmarking.runs.interfaces import Run
from benchmarking.runs.real_data.cosc_341.metrics import (
    calculate_inter_homogeneity_score,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import InsightOutput, Insight
from benchmarking.simulation.simulation_set import SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class ConcentrateTimeDiversifyG2YL(Run):
    """
    This run focuses on the scenario of concentrating timeslots, diversifying all genders with min 2 (female > non-binary > male > no answer), and diversifying based on year level (third year vs. graduate students). This correspond with scenario 2 for the COSC 341 data.
    """

    TEAM_SIZE = 4
    CLASS_SIZE = 175
    MAX_TIME = 1000000
    MAX_KEEP = 30
    MAX_SPREAD = 100
    MAX_ITERATE = 250

    def start(self, num_trials: int = 1, compute_metrics: bool = False):
        scenario = ConcentrateTimeSlotDiversifyAllGenderMin2DiversifyYearLevel()

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
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
                    ScenarioAttribute.GENDER.value: [gender.value for gender in Gender],
                }
            ),
        }

        cache_key = "real_data/cosc_341/concentrate_time_diversify_g2_yl"
        student_provider = COSC341W2021T2AnsweredSurveysStudentProvider()
        simulation_settings = SimulationSettings(
            num_teams=math.ceil(self.CLASS_SIZE / self.TEAM_SIZE),
            student_provider=student_provider,
            scenario=scenario,
            cache_key=cache_key,
        )

        artifacts = SimulationSet(
            settings=simulation_settings,
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
                                f"api/ai/external_algorithms/group_matcher_algorithm/group-matcher/inpData/{self.CLASS_SIZE}-generated.csv",
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
        ).run(num_runs=1)

        artifacts.update(
            SimulationSet(
                settings=simulation_settings,
                algorithm_set={
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_TIME=self.MAX_TIME,
                            MAX_KEEP=self.MAX_KEEP,
                            MAX_SPREAD=self.MAX_SPREAD,
                            MAX_ITERATE=self.MAX_ITERATE,
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
                            x_data=[self.CLASS_SIZE],
                            y_data=[value],
                            name=algorithm_name,
                        )
                    else:
                        graph_data[metric_name][algorithm_name].x_data.append(
                            self.CLASS_SIZE
                        )
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

            # Calculate Inter-Homogeneity for gender
            print("GenderInterHomogeneity", end="")
            calculate_inter_homogeneity_score(artifacts, ScenarioAttribute.GENDER.value)

            # Calculate Inter-Homogeneity for year level
            print("YearLevelInterHomogeneity", end="")
            calculate_inter_homogeneity_score(
                artifacts, ScenarioAttribute.YEAR_LEVEL.value
            )

            # Calculate Inter-Homogeneity for timeslots
            print("TimeslotLevelInterHomogeneity", end="")
            calculate_inter_homogeneity_score(
                artifacts, ScenarioAttribute.TIMESLOT_AVAILABILITY.value
            )


if __name__ == "__main__":
    typer.run(ConcentrateTimeDiversifyG2YL().start)
