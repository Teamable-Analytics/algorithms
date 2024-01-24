from pathlib import Path
from typing import Dict

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    WeightAlgorithmConfig,
    DoubleRoundRobinAlgorithmConfig,
    GroupMatcherAlgorithmConfig,
    RandomAlgorithmConfig,
)
from api.models.enums import AlgorithmType
from api.models.student import Student
from api.models.team import TeamShell
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.metrics.average_timeslot_coverage import (
    AverageTimeslotCoverage,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.runs.interfaces import Run
from benchmarking.evaluations.scenarios.concentrate_timeslot_and_diversify_gender_min_2_female import (
    ConcentrateTimeslotAndDiversifyGenderMin2Female,
)
from benchmarking.runs.timeslot_and_diversify_gender_min_2.custom_student_provider import (
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


class TimeSlotAndDiversifyGenderMin2(Run):
    TEAM_SIZE = 4

    def start(self, num_trials: int = 100, generate_graphs: bool = False):
        scenario = ConcentrateTimeslotAndDiversifyGenderMin2Female(max_num_choices=5)

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
            "AverageTimeslotCoverage": AverageTimeslotCoverage(
                available_timeslots=list(range(10)),
            ),
        }
        simulation_sets = {}

        class_sizes = [20, 100, 240, 500, 1000]
        # class_sizes = [20, 40, 60, 80, 100]

        for class_size in class_sizes:
            print("CLASS SIZE /", class_size)
            student_provider = TimeslotCustomStudentProvider(class_size)

            simulation_settings = SimulationSettings(
                num_teams=class_size // self.TEAM_SIZE,
                student_provider=student_provider,
                scenario=scenario,
                cache_key=f"timeslot_stuff/class_size_{class_size}",
            )

            deterministic_artifacts = SimulationSet(
                settings=simulation_settings,
                algorithm_set={
                    AlgorithmType.WEIGHT: [
                        WeightAlgorithmConfig(),
                    ],
                    AlgorithmType.GROUP_MATCHER: [
                        GroupMatcherAlgorithmConfig(
                            csv_output_path=Path.cwd().parent.parent.parent
                            / f"api/ai/group_matcher_algorithm/group-matcher/inpData/{ class_size }-generated.csv",
                            group_matcher_run_path=Path.cwd().parent.parent.parent
                            / "api/ai/group_matcher_algorithm/group-matcher/run.py",
                        ),
                    ],
                    AlgorithmType.DRR: [DoubleRoundRobinAlgorithmConfig(utility_function=additive_utility_function)],
                },
            ).run(num_runs=1)
            simulation_sets[class_size] = deterministic_artifacts

            probabilistic_artifacts = SimulationSet(
                settings=simulation_settings,
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
            simulation_sets[class_size].update(probabilistic_artifacts)

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
    typer.run(TimeSlotAndDiversifyGenderMin2().start)
