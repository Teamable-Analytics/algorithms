import math

from benchmarking.data.interfaces import MockStudentProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
)
from benchmarking.evaluations.metrics.average_gini_index_multi_attribute import (
    AverageGiniIndexMultiAttribute,
)
from benchmarking.evaluations.metrics.num_requirements_satisfied import (
    NumRequirementsSatisfied,
)
from benchmarking.evaluations.metrics.num_teams_meeting_requirements import (
    NumTeamsMeetingRequirements,
)
from benchmarking.evaluations.scenarios.concentrate_all_attributes import (
    ConcentrateAllAttributes,
)
from benchmarking.simulation.simulation import Simulation
from models.enums import ScenarioAttribute, Gender


def run_concentrate_all_attributes():
    """
    Goal: Run concentrate all attributes scenario, measure average gini index across all attributes
    """

    # Defining our changing x-values (in the graph sense)
    class_sizes = [100, 150, 200, 250, 300]
    num_trials = 10
    ratio_of_female_students = 0.5
    races = [
        "African",
        "European",
        "East Asian",
        "South Asian",
        "South East Asian",
        "First Nations or Indigenous",
        "Hispanic or Latin American",
        "Middle Eastern",
        "Other",
    ]

    for class_size in class_sizes:
        print("CLASS SIZE /", class_size)

        number_of_teams = math.ceil(class_size / 5)

        # set up either mock or real data
        student_provider_settings = MockStudentProviderSettings(
            number_of_students=class_size,
            number_of_friends=4,
            number_of_enemies=1,
            friend_distribution="cluster",
            attribute_ranges={
                ScenarioAttribute.AGE.value: list(range(20, 24)),
                ScenarioAttribute.GENDER.value: [
                    (Gender.MALE, 1 - ratio_of_female_students),
                    (Gender.FEMALE, ratio_of_female_students),
                ],
                ScenarioAttribute.GPA.value: list(range(60, 100)),
                ScenarioAttribute.RACE.value: list(range(len(races))),
                ScenarioAttribute.MAJOR.value: list(range(1, 4)),
                ScenarioAttribute.YEAR_LEVEL.value: list(range(3, 5)),
                ScenarioAttribute.PROJECT_PREFERENCES.value: [1, 2, 3],
            },
            num_values_per_attribute={
                ScenarioAttribute.PROJECT_PREFERENCES.value: 3,
            },
        )

        simulation_outputs = Simulation(
            num_teams=number_of_teams,
            scenario=ConcentrateAllAttributes(),
            student_provider=MockStudentProvider(student_provider_settings),
            metrics=[
                AverageGiniIndexMultiAttribute(
                    attributes=[
                        ScenarioAttribute.AGE.value,
                        ScenarioAttribute.GENDER.value,
                        ScenarioAttribute.GPA.value,
                        ScenarioAttribute.RACE.value,
                        ScenarioAttribute.MAJOR.value,
                        ScenarioAttribute.YEAR_LEVEL.value,
                    ]
                ),
                NumRequirementsSatisfied(),
                NumTeamsMeetingRequirements(),
            ],
        ).run(num_runs=num_trials)

        print(
            "=>",
            Simulation.average_metric(
                simulation_outputs, "AverageGiniIndexMultiAttribute"
            ),
        )
        print(
            "=>",
            Simulation.average_metric(simulation_outputs, "NumRequirementsSatisfied"),
        )
        print(
            "=>",
            Simulation.average_metric(
                simulation_outputs, "NumTeamsMeetingRequirements"
            ),
        )


if __name__ == "__main__":
    run_concentrate_all_attributes()
