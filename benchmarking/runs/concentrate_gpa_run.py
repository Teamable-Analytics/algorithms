import math

from benchmarking.data.interfaces import MockStudentProviderSettings
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
        ).run(num_runs=num_trials)


if __name__ == "__main__":
    concentrate_gpa_run()
