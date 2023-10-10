import math

import typer

from api.models.enums import ScenarioAttribute, Gender, Gpa, Age, Race
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProviderSettings, MockStudentProvider
from benchmarking.evaluations.goals import DiversityGoal
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.metrics.average_gini_index import AverageGiniIndex
from benchmarking.evaluations.metrics.average_gini_index_multi_attribute import AverageGiniIndexMultiAttribute
from benchmarking.evaluations.metrics.maximum_gini_index import MaximumGiniIndex
from benchmarking.evaluations.metrics.minimum_gini_index import MinimumGiniIndex
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.multiple_tokenization_goals import MultipleTokenizationGoals
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.simulation import Simulation


def concentrate_multiple_max_3(num_trials: int = 10):
    """
    Goal: Run a scenario with multiple tokenization constraints to benchmark the algorithm
    """

    # Defining our changing x-values (in the graph sense)
    class_sizes = list(range(50, 501, 50))
    num_trials = 10
    ratio_of_european_students = 0.45
    ratio_of_middle_eastern_students = 0.25
    ratio_of_african_students = 0.15
    ratio_of_other_students = 1 - ratio_of_european_students - ratio_of_middle_eastern_students - ratio_of_african_students
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
                    (Race.Other, ratio_of_other_students)
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
                ]
            },
        )

        scenario = MultipleTokenizationGoals(value_of_age=Age._20.value, value_of_gpa=Gpa.B.value, value_of_race=Race.Middle_Eastern.value)

        simulation_outputs = Simulation(
            num_teams=number_of_teams,
            scenario=scenario,
            student_provider=MockStudentProvider(student_provider_settings),
            metrics=[
                AverageGiniIndexMultiAttribute(attributes=[
                    ScenarioAttribute.RACE.value,
                    ScenarioAttribute.GPA.value,
                    ScenarioAttribute.AGE.value
                ]),
                PrioritySatisfaction(
                    goals_to_priorities(
                        [
                            goal
                            for goal in scenario.goals
                            if isinstance(goal, DiversityGoal)
                        ]
                    ),
                    False,
                ),
            ],
        ).run(num_runs=num_trials)

        average_ginis = Simulation.average_metric(
            simulation_outputs, "AverageGiniIndexMultiAttribute"
        )
        average_runtimes = Simulation.average_metric(
            simulation_outputs, Simulation.KEY_RUNTIMES
        )
        satisfied_priorities = Simulation.average_metric(
            simulation_outputs, "PrioritySatisfaction"
        )
        metrics = [
            average_runtimes,
            average_ginis,
            satisfied_priorities,
        ]

        # Data processing for graph
        for i, metric in enumerate(metrics):
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

    line_graph(
        LineGraphMetadata(
            x_label="Class size",
            y_label="Run time (seconds)",
            title="Multiple Tokenization Goals Runtimes",
            data=list(graph_runtime_dict.values()),
            description=None,
            y_lim=None,
            x_lim=None,
        )
    )

    line_graph(
        LineGraphMetadata(
            x_label="Class size",
            y_label="Average Gini Index",
            title="Multiple Tokenization Goals Average Gini Index",
            data=list(graph_avg_gini_dict.values()),
            description=None,
            y_lim=None,
            x_lim=None,
        )
    )

    line_graph(
        LineGraphMetadata(
            x_label="Class size",
            y_label="Priorities Satisfied",
            title="Multiple Tokenization Goals Satisfied Priorities",
            data=list(graph_priority_dict.values()),
            description=None,
            y_lim=None,
            x_lim=None,
        )
    )


if __name__ == "__main__":
    typer.run(concentrate_multiple_max_3)
