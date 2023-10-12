from typing import List, Dict

import jsonpickle

from api.models.enums import AlgorithmType, ScenarioAttribute, Gender
from benchmarking.evaluations.goals import DiversityGoal
from benchmarking.evaluations.graphing.graph_metadata import GraphAxisRange, GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.average_gini_index import AverageGiniIndex
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.maximum_gini_index import MaximumGiniIndex
from benchmarking.evaluations.metrics.minimum_gini_index import MinimumGiniIndex
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.metrics.utils.team_calculations import (
    is_happy_team_1shp_friend,
)
from benchmarking.evaluations.scenarios.diversify_gender_min_2_female import (
    DiversifyGenderMin2Female,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities

if __name__ == "__main__":
    scenario = DiversifyGenderMin2Female(value_of_female=Gender.FEMALE.value)
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

    # Defines the files to read
    scenarios = [
        "diversify-gender",
        "three-tokenization-priority",
    ]
    mutations = [
        "social",
        "baseline",
        "mutate-local-max",
        "epsilon-0.05",
        "epsilon-0.25",
        "epsilon-1",
        "robinhood",
        "robinhood-holistic",
    ]

    # Produce a set of graphs for each scenario
    for scenario in scenarios:
        graph_runtime_list: List[GraphData] = []
        graph_avg_gini_list: List[GraphData] = []
        graph_min_gini_list: List[GraphData] = []
        graph_max_gini_list: List[GraphData] = []
        graph_priority_list: List[GraphData] = []
        graph_social_list: List[GraphData] = []

        if scenario == scenarios[0]:
            graph_lists: List[List[GraphData]] = [
                graph_runtime_list,
                graph_avg_gini_list,
                graph_min_gini_list,
                graph_max_gini_list,
                graph_priority_list,
                graph_social_list,
            ]
        else:
            graph_lists: List[List[GraphData]] = [
                graph_runtime_list,
                graph_avg_gini_list,
                graph_priority_list,
                graph_social_list,
            ]

        # Read the data from the files
        for mutation in mutations:
            try:
                with open(f"{scenario}-{mutation}.json", "r") as f:
                    json_graph_dicts: List[Dict[str, GraphData]] = jsonpickle.decode(
                        f.read()
                    )
            except FileNotFoundError:
                continue

            for graph_dict in json_graph_dicts:
                for algorithm_type, graph_data in graph_dict.items():
                    graph_data.name = graph_data.name.replace("_", " ").title()
                    if AlgorithmType.PRIORITY_NEW.name in algorithm_type:
                        if mutation == "baseline":
                            graph_data.legend_subtitle = "(Random)"
                        else:
                            graph_data.legend_subtitle = (
                                f'({mutation.replace("-", " ").title()})'
                            )

            for i in range(len(json_graph_dicts)):
                graph_lists[i].extend(list(json_graph_dicts[i].values()))

        # Graph the data
        scenario_title = (
            "Diversify Gender With Min of Two"
            if scenario == scenarios[0]
            else "Three Tokenization Constraints"
        )
        graph_descriptions = "Priority (300 iterations, 1000sec)\nStudents (2 friends, 2 enemies, clustered)"

        save_graphs = True

        if len(graph_runtime_list) != 0:
            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Run time (seconds)",
                    title=f"{scenario_title} Runtimes",
                    data=list(graph_runtime_list),
                    description=graph_descriptions,
                    y_lim=None,
                    x_lim=None,
                    num_minor_ticks=None,
                    save_graph=save_graphs,
                )
            )

        if len(graph_avg_gini_list) != 0:
            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Average Gini Index",
                    title=f"{scenario_title} Average Gini Index",
                    data=list(graph_avg_gini_list),
                    description=graph_descriptions,
                    y_lim=GraphAxisRange(
                        *metrics["AverageGiniIndex"].theoretical_range
                    ),
                    x_lim=None,
                    num_minor_ticks=None,
                    save_graph=save_graphs,
                )
            )

        if len(graph_min_gini_list) != 0:
            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Minimum Gini Index",
                    title=f"{scenario_title} Minimum Gini",
                    data=list(graph_min_gini_list),
                    description=graph_descriptions,
                    y_lim=GraphAxisRange(*metrics["MinGiniIndex"].theoretical_range),
                    x_lim=None,
                    num_minor_ticks=None,
                    save_graph=save_graphs,
                )
            )

        if len(graph_max_gini_list) != 0:
            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Maximum Gini Index",
                    title=f"{scenario_title} Max Gini",
                    data=list(graph_max_gini_list),
                    description=graph_descriptions,
                    y_lim=GraphAxisRange(*metrics["MaxGiniIndex"].theoretical_range),
                    x_lim=None,
                    num_minor_ticks=None,
                    save_graph=save_graphs,
                )
            )

        if len(graph_priority_list) != 0:
            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Priorities Satisfied",
                    title=f"{scenario_title} Satisfied Priorities",
                    data=list(graph_priority_list),
                    description=graph_descriptions,
                    y_lim=GraphAxisRange(-0.1, 1.1),
                    x_lim=None,
                    num_minor_ticks=None,
                    save_graph=save_graphs,
                )
            )

        if len(graph_social_list) != 0:
            line_graph(
                LineGraphMetadata(
                    x_label="Class size",
                    y_label="Social Satisfaction",
                    title=f"{scenario_title} Social Satisfaction",
                    data=list(graph_social_list),
                    description=graph_descriptions
                    + "\nRatio of teams with at least 1 SHP",
                    y_lim=GraphAxisRange(-0.0, 0.06),
                    x_lim=None,
                    num_minor_ticks=None,
                    save_graph=save_graphs,
                )
            )
