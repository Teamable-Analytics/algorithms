import math
from typing import Dict, List

import typer

from api.ai.interfaces.algorithm_config import (
    RandomAlgorithmConfig,
    SocialAlgorithmConfig,
    WeightAlgorithmConfig,
    PriorityAlgorithmConfig,
)
from api.ai.priority_algorithm.mutations import mutate_local_max, mutate_random_swap
from api.models.enums import ScenarioAttribute, Gpa, Age, Race, AlgorithmType
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProviderSettings,
    MockStudentProvider,
)
from benchmarking.evaluations.goals import DiversityGoal
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.average_gini_index_multi_attribute import (
    AverageGiniIndexMultiAttribute,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.three_tokenization_constraints import (
    ThreeTokenizationConstraints,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings


def three_tokenization_constraints(num_trials: int = 10, generate_graphs: bool = True):
    """
    Goal: Run a scenario with three tokenization constraints:
    concentrate GPA max three, diversify race min two, and concentrate age max three.
    """

    # Defining our changing x-values (in the graph sense)
    class_sizes = list(range(50, 501, 50))
    ratio_of_european_students = 0.45
    ratio_of_middle_eastern_students = 0.25
    ratio_of_african_students = 0.15
    ratio_of_other_students = (
        1
        - ratio_of_european_students
        - ratio_of_middle_eastern_students
        - ratio_of_african_students
    )
    ratio_of_a_students = 0.25
    ratio_of_b_students = 0.50
    ratio_of_c_students = 0.25
    ratio_of_age_18_students = 0.10
    ratio_of_age_19_students = 0.40
    ratio_of_age_20_students = 0.30
    ratio_of_age_21_students = 0.20

    graph_runtime_dict = {}
    graph_avg_gini_dict = {}
    graph_priority_dict = {}
    graph_dicts = [
        graph_runtime_dict,
        graph_avg_gini_dict,
        graph_priority_dict,
    ]

    scenario = ThreeTokenizationConstraints(
        value_of_age=Age._20.value,
        value_of_gpa=Gpa.B.value,
        value_of_race=Race.Middle_Eastern.value,
    )

    metrics: Dict[str, TeamSetMetric] = {
        "AverageGiniIndexMultiAttribute": AverageGiniIndexMultiAttribute(
            attributes=[
                ScenarioAttribute.RACE.value,
                ScenarioAttribute.GPA.value,
                ScenarioAttribute.AGE.value,
            ]
        ),
        "PrioritySatisfaction": PrioritySatisfaction(
            goals_to_priorities(
                [goal for goal in scenario.goals if isinstance(goal, DiversityGoal)]
            ),
            False,
        ),
    }

    artifacts: Dict[int, SimulationSetArtifact] = {}

    for class_size in class_sizes:
        print("CLASS SIZE /", class_size)

        number_of_teams = math.ceil(class_size / 5)

        # set up either mock or real data
        student_provider_settings = MockStudentProviderSettings(
            number_of_students=class_size,
            attribute_ranges={
                ScenarioAttribute.RACE.value: [
                    (Race.European, ratio_of_european_students),
                    (Race.Middle_Eastern, ratio_of_middle_eastern_students),
                    (Race.African, ratio_of_african_students),
                    (Race.Other, ratio_of_other_students),
                ],
                ScenarioAttribute.GPA.value: [
                    (Gpa.A, ratio_of_a_students),
                    (Gpa.B, ratio_of_b_students),
                    (Gpa.C, ratio_of_c_students),
                ],
                ScenarioAttribute.AGE.value: [
                    (Age._18, ratio_of_age_18_students),
                    (Age._19, ratio_of_age_19_students),
                    (Age._20, ratio_of_age_20_students),
                    (Age._21, ratio_of_age_21_students),
                ],
            },
        )

        simulation_set_artifact = SimulationSet(
            settings=SimulationSettings(
                num_teams=number_of_teams,
                scenario=scenario,
                student_provider=MockStudentProvider(student_provider_settings),
                cache_key=f"three_tokenization_constraints_{number_of_teams}",
            ),
            algorithm_set={
                AlgorithmType.RANDOM: [RandomAlgorithmConfig()],
                AlgorithmType.SOCIAL: [SocialAlgorithmConfig()],
                AlgorithmType.WEIGHT: [WeightAlgorithmConfig()],
                AlgorithmType.PRIORITY: [
                    PriorityAlgorithmConfig(),
                    PriorityAlgorithmConfig(
                        name="local_max",
                        MUTATIONS=[(mutate_local_max, 1), (mutate_random_swap, 2)],
                    ),
                ],
            },
        ).run(num_runs=num_trials)
        artifacts[class_size] = simulation_set_artifact

    if generate_graphs:
        for class_size, artifact in artifacts.items():
            insight_set: Dict[str, Dict[str, List[float]]] = Insight.get_output_set(
                artifact=artifact, metrics=list(metrics.values())
            )

            average_ginis = Insight.average_metric(
                insight_set, "AverageGiniIndexMultiAttribute"
            )
            average_runtimes = Insight.average_metric(insight_set, Insight.KEY_RUNTIMES)
            satisfied_priorities = Insight.average_metric(
                insight_set, "PrioritySatisfaction"
            )

            metric_values = [
                average_runtimes,
                average_ginis,
                satisfied_priorities,
            ]

            # Data processing for graph
            for i, metric in enumerate(metric_values):
                for name, data in metric.items():
                    if name not in graph_dicts[i]:
                        graph_dicts[i][name] = GraphData(
                            x_data=[class_size],
                            y_data=[data],
                            name=name,
                        )
                    else:
                        graph_dicts[i][name].x_data.append(class_size)
                        graph_dicts[i][name].y_data.append(data)

        line_graph(
            LineGraphMetadata(
                x_label="Class size",
                y_label="Run time (seconds)",
                title="Three Tokenization Constraints Runtimes",
                data=list(graph_runtime_dict.values()),
            )
        )

        line_graph(
            LineGraphMetadata(
                x_label="Class size",
                y_label="Average Gini Index",
                title="Three Tokenization Constraints Average Gini Index",
                data=list(graph_avg_gini_dict.values()),
            )
        )

        line_graph(
            LineGraphMetadata(
                x_label="Class size",
                y_label="Priorities Satisfied",
                title="Three Tokenization Constraints Satisfied Priorities",
                data=list(graph_priority_dict.values()),
            )
        )


if __name__ == "__main__":
    typer.run(three_tokenization_constraints)
