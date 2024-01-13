from typing import Dict

from benchmarking.data.interfaces import StudentProvider
from benchmarking.evaluations.interfaces import Scenario
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.runs.simple_runs.custom_student_providers import (
    CustomTwelveStudentProvider,
    CustomFifteenStudentProvider,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities


class SimpleRunData:
    class_sizes = [12, 15]
    num_teams = 3
    student_providers: Dict[int, StudentProvider] = {
        12: CustomTwelveStudentProvider(),
        15: CustomFifteenStudentProvider(),
    }

    @staticmethod
    def get_metrics(scenario: Scenario):
        return {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
        }

    # Ranges
    max_keep_range = list(range(1, 16, 2))
    max_spread_range = list(range(1, 16, 2))
    max_iterations_range = [1, 3, 5, 10, 15]
