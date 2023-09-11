import math

from benchmarking.data.interfaces import MockStudentProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProvider
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.utils.team_calculations import is_happy_team_allhp_friend
from benchmarking.evaluations.scenarios.include_social_friends import (
    IncludeSocialFriends,
)
from benchmarking.simulation.simulation import Simulation


def run_include_social_friends():
    """
    Goal: Run including social friends, measure average social satisfied team
    (a team socially satisfied when all member is happy)
    """

    # Defining our changing x-values (in the graph sense)
    class_sizes = [100, 150, 200, 250, 300]
    num_trials = 10

    for class_size in class_sizes:
        print("CLASS SIZE /", class_size)

        number_of_teams = math.ceil(class_size / 5)

        # set up either mock or real data
        student_provider_settings = MockStudentProviderSettings(
            number_of_students=class_size,
            number_of_friends=2,
            number_of_enemies=2,
            friend_distribution="cluster",
        )

        simulation_outputs = Simulation(
            num_teams=number_of_teams,
            scenario=IncludeSocialFriends(),
            student_provider=MockStudentProvider(student_provider_settings),
            metrics=[
                AverageSocialSatisfaction(metric_function=is_happy_team_allhp_friend),
            ],
        ).run(num_runs=num_trials)

        print(
            "=>",
            Simulation.average_metric(simulation_outputs, "AverageSocialSatisfaction"),
        )


if __name__ == "__main__":
    run_include_social_friends()
