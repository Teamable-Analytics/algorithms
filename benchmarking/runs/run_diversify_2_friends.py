import math

from benchmarking.data.interfaces import MockStudentProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProvider
from benchmarking.evaluations.metrics.average_gini_index import AverageGiniIndex
from benchmarking.evaluations.metrics.num_requirements_satisfied import (
    NumRequirementsSatisfied,
)
from benchmarking.evaluations.metrics.num_teams_meeting_requirements import (
    NumTeamsMeetingRequirements,
)
from benchmarking.evaluations.scenarios.diversify_social_min_2_friends import (
    DiversifySocialMin2Friends,
)
from benchmarking.simulation.simulation import Simulation
from models.enums import ScenarioAttribute, Relationship


def copy_of_test_saved_run():
    """
    Goal: Run diversify gender scenario, measure average gini index
    """

    # Defining our changing x-values (in the graph sense)
    class_sizes = [100, 150, 200, 250, 300]
    num_trials = 10
    ratio_of_friends = 0.5
    ratio_of_enemies = 0.1

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
                ScenarioAttribute.SOCIAL.value: [
                    (Relationship.FRIEND, ratio_of_friends),
                    (Relationship.ENEMY, ratio_of_enemies),
                    (Relationship.DEFAULT, 1 - ratio_of_friends - ratio_of_enemies),
                ],
                ScenarioAttribute.PROJECT_PREFERENCES.value: [1, 2, 3],
            },
            num_values_per_attribute={
                ScenarioAttribute.PROJECT_PREFERENCES.value: 3,
            },
        )

        simulation_outputs = Simulation(
            num_teams=number_of_teams,
            scenario=DiversifySocialMin2Friends(
                value_of_friend=Relationship.FRIEND.value
            ),
            student_provider=MockStudentProvider(student_provider_settings),
            metrics=[
                AverageGiniIndex(attribute=ScenarioAttribute.SOCIAL.value),
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


if __name__ == "__main__":
    copy_of_test_saved_run()
