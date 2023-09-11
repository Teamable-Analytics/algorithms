import math

from benchmarking.data.interfaces import MockStudentProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProvider
from benchmarking.evaluations.metrics.average_gini_index import AverageGiniIndex
from benchmarking.evaluations.metrics.maximum_gini_index import MaximumGiniIndex
from benchmarking.evaluations.metrics.minimum_gini_index import MinimumGiniIndex
from benchmarking.evaluations.scenarios.concentrate_gpa import ConcentrateGPA
from benchmarking.simulation.simulation import Simulation
from models.enums import ScenarioAttribute, Gpa


def concentrate_gpa_run():
    """
    Goal: Run concentrate GPA scenario, measure average GPA difference within group
    """

    # Define changing values
    class_sizes = [50, 150, 200, 250, 300, 350, 400]
    num_trials = 10
    ratio_of_a_students = 0.25
    ratio_of_b_students = 0.50
    ratio_of_c_students = 0.25

    for class_size in class_sizes:
        print("CLASS SIZE /", class_size)

        number_of_teams = math.ceil(class_size / 5)

        student_provider_settings = MockStudentProviderSettings(
            number_of_students=class_size,
            attribute_ranges={
                ScenarioAttribute.GPA.value: [
                    (Gpa.A, ratio_of_a_students),
                    (Gpa.B, ratio_of_b_students),
                    (Gpa.C, ratio_of_c_students),
                ]
            },
        )

        simulation_outputs = Simulation(
            num_teams=number_of_teams,
            scenario=ConcentrateGPA(),
            student_provider=MockStudentProvider(student_provider_settings),
            metrics=[
                AverageGiniIndex(attribute=ScenarioAttribute.GPA.value),
                MaximumGiniIndex(attribute=ScenarioAttribute.GPA.value),
                MinimumGiniIndex(attribute=ScenarioAttribute.GPA.value),
            ],
        ).run(num_runs=num_trials)

        print(
            "Average Gini Index for GPA =>",
            Simulation.average_metric(simulation_outputs, "AverageGiniIndex"),
        )
        print(
            "Maximum Gini Index for GPA =>",
            Simulation.average_metric(simulation_outputs, "MaximumGiniIndex"),
        )
        print(
            "Minimum Gini Index for GPA =>",
            Simulation.average_metric(simulation_outputs, "MinimumGiniIndex"),
        )


if __name__ == "__main__":
    concentrate_gpa_run()
