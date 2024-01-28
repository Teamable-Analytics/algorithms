import math
import os
from pathlib import Path
from typing import Dict

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    WeightAlgorithmConfig,
    GroupMatcherAlgorithmConfig,
    RandomAlgorithmConfig,
)
from api.models.enums import AlgorithmType
from benchmarking.data.real_data.cosc341_w2022_provider.providers import (
    COSC341W2021T2AnsweredSurveysStudentProvider,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.metrics.average_timeslot_coverage import (
    AverageTimeslotCoverage,
)
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineSimilarity
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.concentrate_timeslot_diversify_gender_min_2_and_diversify_year_level import (
    ConcentrateTimeSlotDiversifyGenderMin2AndDiversifyYearLevel,
    DiversifyGenderMin2ConcentrateTimeSlotAndDiversifyYearLevel,
)
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import InsightOutput, Insight
from benchmarking.simulation.simulation_set import SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class ConcentrateTimeslotDiversifyGenderAndStudentLevel(Run):
    TEAM_SIZE = 4

    def start(self, num_trials: int = 1, generate_graphs: bool = True):
        scenario_1 = ConcentrateTimeSlotDiversifyGenderMin2AndDiversifyYearLevel(
            max_num_choices=6
        )
        scenario_2 = DiversifyGenderMin2ConcentrateTimeSlotAndDiversifyYearLevel(
            max_num_choices=6
        )

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario_1.goals),
                False,
            ),
            "AverageTimeslotCoverage": AverageTimeslotCoverage(
                available_timeslots=list(range(10)),
            ),
            "AverageCosineSimilarity": AverageCosineSimilarity(),
        }

        student_provider = COSC341W2021T2AnsweredSurveysStudentProvider()
        simulation_settings_1 = SimulationSettings(
            num_teams=math.ceil(175 / self.TEAM_SIZE),
            student_provider=student_provider,
            scenario=scenario_1,
            cache_key=f"real_data/cosc_341/concentrate_timeslot_diversify_gender_and_student_level",
        )

        simulation_settings_2 = SimulationSettings(
            num_teams=math.ceil(175 / self.TEAM_SIZE),
            student_provider=student_provider,
            scenario=scenario_2,
            cache_key=f"real_data/cosc_341/concentrate_timeslot_diversify_gender_and_student_level",
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
                                f"api/ai/group_matcher_algorithm/group-matcher/inpData/{175}-generated.csv"
                            )
                        ),
                        group_matcher_run_path=os.path.abspath(
                            os.path.join(
                                os.path.dirname(__file__),
                                "../../../..",
                                "api/ai/group_matcher_algorithm/group-matcher/run.py"
                            )
                        )
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
                            MAX_KEEP=15,
                            MAX_SPREAD=30,
                            MAX_ITERATE=30,
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
                            MAX_KEEP=15,
                            MAX_SPREAD=30,
                            MAX_ITERATE=30,
                            name="Switched Order Priority"
                        ),
                    ],
                    AlgorithmType.RANDOM: [
                        RandomAlgorithmConfig(),
                    ],
                },
            ).run(num_runs=num_trials)
        )

        if generate_graphs:
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
                            x_data=[120],
                            y_data=[value],
                            name=algorithm_name,
                        )
                    else:
                        graph_data[metric_name][algorithm_name].x_data.append(120)
                        graph_data[metric_name][algorithm_name].y_data.append(value)

            for metric_name in metrics.keys():
                y_label = metrics[metric_name].name
                y_lim = GraphAxisRange(0, 1.1)
                line_graph(
                    LineGraphMetadata(
                        x_label="Class Size",
                        y_label=y_label,
                        title="Timeslot - Diversity Scenarios",
                        data=list(graph_data[metric_name].values()),
                        y_lim=y_lim,
                    ),
                )


if __name__ == "__main__":
    typer.run(ConcentrateTimeslotDiversifyGenderAndStudentLevel().start)
