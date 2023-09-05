import math

from models.enums import ScenarioAttribute, Gender
from benchmarking.data.interfaces import MockStudentProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
)
from benchmarking.evaluations.metrics.average_gini_index import (
    AverageGiniIndex,
)
from benchmarking.evaluations.metrics.num_requirements_satisfied import (
    NumRequirementsSatisfied,
)
from benchmarking.evaluations.metrics.num_teams_meeting_requirements import (
    NumTeamsMeetingRequirements,
)
from benchmarking.evaluations.scenarios.diversify_gender_min_2_female import (
    DiversifyGenderMin2Female,
)
from benchmarking.simulation.simulation import Simulation


def test_saved_run():
    """
    Goal: Run diversify gender scenario, measure average gini index
    """

    # Defining our changing x-values (in the graph sense)
    class_sizes = [100, 150, 200, 250, 300]
    num_trials = 10
    ratio_of_female_students = 0.5

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
                ScenarioAttribute.GENDER.value: [
                    (Gender.MALE, 1 - ratio_of_female_students),
                    (Gender.FEMALE, ratio_of_female_students),
                ],
                ScenarioAttribute.PROJECT_PREFERENCES.value: [1, 2, 3],
            },
            num_values_per_attribute={
                ScenarioAttribute.PROJECT_PREFERENCES.value: 3,
            },
        )

        simulation_outputs = Simulation(
            num_teams=number_of_teams,
            scenario=DiversifyGenderMin2Female(value_of_female=Gender.FEMALE.value),
            student_provider=MockStudentProvider(student_provider_settings),
            metrics=[
                AverageGiniIndex(attribute=ScenarioAttribute.GENDER.value),
                NumRequirementsSatisfied(),
                NumTeamsMeetingRequirements(),
            ],
        ).run(num_runs=num_trials)

        print("=>", Simulation.average_metric(simulation_outputs, "AverageGiniIndex"))
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
