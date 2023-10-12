import math
from typing import Dict, List

import jsonpickle
import typer

from benchmarking.evaluations.goals import DiversityGoal
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
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
from benchmarking.evaluations.metrics.utils.team_calculations import (
    is_happy_team_1shp_friend,
)
from benchmarking.evaluations.scenarios.diversify_gender_min_2_female import (
    DiversifyGenderMin2Female,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.simulation import Simulation


def diversify_gender_min_2(num_trials: int = 10):
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
    graph_social_dict = {}
    graph_dicts = [
        graph_runtime_dict,
        graph_avg_gini_dict,
        graph_min_gini_dict,
        graph_max_gini_dict,
        graph_priority_dict,
        graph_social_dict,
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
        "AverageSocialSatisfaction": AverageSocialSatisfaction(
            is_happy_team_1shp_friend
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
            number_of_friends=2,
            number_of_enemies=2,
            friend_distribution="cluster",
        )

        simulation_outputs = Simulation(
            num_teams=number_of_teams,
            scenario=scenario,
            student_provider=MockStudentProvider(student_provider_settings),
            metrics=list(metrics.values()),
            algorithm_types=[
                AlgorithmType.PRIORITY_NEW,
            ],
        ).run(num_runs=num_trials)

        average_ginis = Simulation.average_metric(
            simulation_outputs, "AverageGiniIndex"
        )
        maximum_ginis = Simulation.average_metric(
            simulation_outputs, "MaximumGiniIndex"
        )
        minimum_ginis = Simulation.average_metric(
            simulation_outputs, "MinimumGiniIndex"
        )
        average_runtimes = Simulation.average_metric(
            simulation_outputs, Simulation.KEY_RUNTIMES
        )
        satisfied_priorities = Simulation.average_metric(
            simulation_outputs, "PrioritySatisfaction"
        )
        friend_satisfaction_priority = Simulation.average_metric(
            simulation_outputs, "AverageSocialSatisfaction"
        )
        metric_values = [
            average_runtimes,
            average_ginis,
            minimum_ginis,
            maximum_ginis,
            satisfied_priorities,
            friend_satisfaction_priority,
        ]

        # Data processing for graph
        for i, metric in enumerate(metric_values):
            for algorithm_type, data in metric.items():
                if algorithm_type not in graph_dicts[i]:
                    graph_dicts[i][algorithm_type] = GraphData(
                        x_data=[class_size],
                        y_data=[data],
                        name=algorithm_type.value,
                        legend_subtitle=(
                            None
                            if algorithm_type != AlgorithmType.PRIORITY_NEW
                            else "mutation type"
                        ),
                    )
                else:
                    graph_dicts[i][algorithm_type].x_data.append(class_size)
                    graph_dicts[i][algorithm_type].y_data.append(data)

    # Save data rather than graph it
    json_string = jsonpickle.encode(graph_dicts)
    with open("diversify-gender-epsilon-1.json", "w+") as f:
        f.write(json_string)

    # with open("json_trash.json", "r") as f:
    #     graph_dicts: List[Dict] = jsonpickle.decode(f.read())
    #
    # graph_runtime_dict = graph_dicts[0]
    # graph_avg_gini_dict = graph_dicts[1]
    # graph_min_gini_dict = graph_dicts[2]
    # graph_max_gini_dict = graph_dicts[3]
    # graph_priority_dict = graph_dicts[4]
    # graph_social_dict = graph_dicts[5]
    #
    # line_graph(
    #     LineGraphMetadata(
    #         x_label="Class size",
    #         y_label="Run time (seconds)",
    #         title="Diversify Gender With Min of Two Runtimes",
    #         data=list(graph_runtime_dict.values()),
    #         description=None,
    #         y_lim=None,
    #         x_lim=None,
    #         num_minor_ticks=None,
    #     )
    # )
    #
    # line_graph(
    #     LineGraphMetadata(
    #         x_label="Class size",
    #         y_label="Average Gini Index",
    #         title="Diversify Gender With Min of Two Average Gini Index",
    #         data=list(graph_dicts[1].values()),
    #         description=None,
    #         y_lim=GraphAxisRange(*metrics["AverageGiniIndex"].theoretical_range),
    #         x_lim=None,
    #         num_minor_ticks=None,
    #     )
    # )
    #
    # line_graph(
    #     LineGraphMetadata(
    #         x_label="Class size",
    #         y_label="Minimum Gini Index",
    #         title="Diversify Gender With Min of Two Minimum Gini",
    #         data=list(graph_min_gini_dict.values()),
    #         description=None,
    #         y_lim=GraphAxisRange(*metrics["MinGiniIndex"].theoretical_range),
    #         x_lim=None,
    #         num_minor_ticks=None,
    #     )
    # )
    #
    # line_graph(
    #     LineGraphMetadata(
    #         x_label="Class size",
    #         y_label="Maximum Gini Index",
    #         title="Diversify Gender With Min of Two Max Gini",
    #         data=list(graph_max_gini_dict.values()),
    #         description=None,
    #         y_lim=GraphAxisRange(*metrics["MaxGiniIndex"].theoretical_range),
    #         x_lim=None,
    #         num_minor_ticks=None,
    #     )
    # )
    #
    # line_graph(
    #     LineGraphMetadata(
    #         x_label="Class size",
    #         y_label="Priorities Satisfied",
    #         title="Diversity Gender With Min of Two Satisfied Priorities",
    #         data=list(graph_priority_dict.values()),
    #         description=None,
    #         y_lim=GraphAxisRange(*metrics["PrioritySatisfaction"].theoretical_range),
    #         x_lim=None,
    #         num_minor_ticks=None,
    #     )
    # )
    #
    # line_graph(
    #     LineGraphMetadata(
    #         x_label="Class size",
    #         y_label="Social Satisfaction",
    #         title="Diversity Gender With Min of Two Social Satisfaction",
    #         data=list(graph_priority_dict.values()),
    #         description="Ratio of teams with at least 1 SHP",
    #         y_lim=None,
    #         x_lim=None,
    #         num_minor_ticks=None,
    #     )
    # )


if __name__ == "__main__":
    typer.run(diversify_gender_min_2)
