import math
from typing import Dict, List

import typer

from benchmarking.evaluations.goals import DiversityGoal
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.maximum_gini_index import MaximumGiniIndex
from benchmarking.evaluations.metrics.minimum_gini_index import MinimumGiniIndex
from api.models.enums import ScenarioAttribute, Gender, AlgorithmType
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.metrics.average_gini_index import (
    AverageGiniIndex,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.diversify_gender_min_2_female import (
    DiversifyGenderMin2Female,
)
from benchmarking.simulation.basic_simulation_set_2 import BasicSimulationSet2
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_settings import SimulationSettings


def diversify_gender_min_2(num_trials: int = 10, generate_graphs: bool = False):
    """
    Goal: Run diversify gender scenario, measure average, min, and max gini index
    """

    # Defining our changing x-values (in the graph sense)
    class_sizes = list(range(50, 501, 50))
    ratio_of_female_students = 0.2

    scenario = DiversifyGenderMin2Female(value_of_female=Gender.FEMALE.value)

    graph_runtime_dict = {}
    graph_avg_gini_dict = {}
    graph_min_gini_dict = {}
    graph_max_gini_dict = {}
    graph_priority_dict = {}
    graph_dicts = [
        graph_runtime_dict,
        graph_avg_gini_dict,
        graph_min_gini_dict,
        graph_max_gini_dict,
        graph_priority_dict,
    ]

    metrics: Dict[str, TeamSetMetric] = {
        "AverageGiniIndex": AverageGiniIndex(attribute=ScenarioAttribute.GENDER.value),
        "MaxGiniIndex": MaximumGiniIndex(attribute=ScenarioAttribute.GENDER.value),
        "MinGiniIndex": MinimumGiniIndex(attribute=ScenarioAttribute.GENDER.value),
        "PrioritySatisfaction": PrioritySatisfaction(
            goals_to_priorities(
                [goal for goal in scenario.goals if isinstance(goal, DiversityGoal)]
            ),
            False,
        ),
    }

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

        # simulation_outputs = BasicSimulationSet(
        #     num_teams=number_of_teams,
        #     scenario=scenario,
        #     student_provider=MockStudentProvider(student_provider_settings),
        #     metrics=list(metrics.values()),
        # ).run(num_runs=num_trials)
        simulation_set_artifact = BasicSimulationSet2(
            settings=SimulationSettings(
                num_teams=number_of_teams,
                scenario=scenario,
                student_provider=MockStudentProvider(student_provider_settings),
                cache_key=f"diversify_gender_min_2_{number_of_teams}",
            )
        ).run(num_runs=num_trials)

        if generate_graphs:
            insight_set: Dict[
                AlgorithmType, Dict[str, List[float]]
            ] = Insight.get_output_set(
                artifact=simulation_set_artifact, metrics=list(metrics.values())
            )

            average_ginis = Insight.average_metric(insight_set, "AverageGiniIndex")
            maximum_ginis = Insight.average_metric(insight_set, "MaximumGiniIndex")
            minimum_ginis = Insight.average_metric(insight_set, "MinimumGiniIndex")
            average_runtimes = Insight.average_metric(insight_set, Insight.KEY_RUNTIMES)
            satisfied_priorities = Insight.average_metric(
                insight_set, "PrioritySatisfaction"
            )

            metric_values = [
                average_runtimes,
                average_ginis,
                minimum_ginis,
                maximum_ginis,
                satisfied_priorities,
            ]

            # Data processing for graph
            for i, metric in enumerate(metric_values):
                for algorithm_type, data in metric.items():
                    if algorithm_type not in graph_dicts[i]:
                        graph_dicts[i][algorithm_type] = GraphData(
                            x_data=[class_size],
                            y_data=[data],
                            name=algorithm_type.value,
                        )
                    else:
                        graph_dicts[i][algorithm_type].x_data.append(class_size)
                        graph_dicts[i][algorithm_type].y_data.append(data)

    if generate_graphs:
        line_graph(
            LineGraphMetadata(
                x_label="Class size",
                y_label="Run time (seconds)",
                title="Diversify Gender With Min of Two Runtimes",
                data=list(graph_runtime_dict.values()),
                description=None,
                y_lim=None,
                x_lim=None,
                num_minor_ticks=None,
            )
        )

        line_graph(
            LineGraphMetadata(
                x_label="Class size",
                y_label="Average Gini Index",
                title="Diversify Gender With Min of Two Average Gini Index",
                data=list(graph_avg_gini_dict.values()),
                description=None,
                y_lim=GraphAxisRange(*metrics["AverageGiniIndex"].theoretical_range),
                x_lim=None,
                num_minor_ticks=None,
            )
        )

        line_graph(
            LineGraphMetadata(
                x_label="Class size",
                y_label="Minimum Gini Index",
                title="Diversify Gender With Min of Two Minimum Gini",
                data=list(graph_min_gini_dict.values()),
                description=None,
                y_lim=GraphAxisRange(*metrics["MinGiniIndex"].theoretical_range),
                x_lim=None,
                num_minor_ticks=None,
            )
        )

        line_graph(
            LineGraphMetadata(
                x_label="Class size",
                y_label="Maximum Gini Index",
                title="Diversify Gender With Min of Two Max Gini",
                data=list(graph_max_gini_dict.values()),
                description=None,
                y_lim=GraphAxisRange(*metrics["MaxGiniIndex"].theoretical_range),
                x_lim=None,
                num_minor_ticks=None,
            )
        )

        line_graph(
            LineGraphMetadata(
                x_label="Class size",
                y_label="Priorities Satisfied",
                title="Diversity Gender With Min of Two Satisfied Priorities",
                data=list(graph_priority_dict.values()),
                description=None,
                y_lim=GraphAxisRange(
                    *metrics["PrioritySatisfaction"].theoretical_range
                ),
                x_lim=None,
                num_minor_ticks=None,
            )
        )


if __name__ == "__main__":
    typer.run(diversify_gender_min_2)
