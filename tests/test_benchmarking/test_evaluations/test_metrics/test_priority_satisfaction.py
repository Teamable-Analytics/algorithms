import statistics
import unittest

from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from tests.test_api.test_ai.test_priority_algorithm.test_mutations.test_local_max import (
    EvenPriority,
    JohnPriority,
)


class TestPrioritySatisfactionMetric(unittest.TestCase):
    @classmethod
    def setUp(cls):
        students = [
            Student(_id=2, name="Steve"),
            Student(_id=4, name="John"),
            Student(_id=5, name="Hailey"),
            Student(_id=6, name="Brenda"),
            Student(_id=8, name="Johan"),
            Student(_id=10, name="Seth"),
        ]
        team_set = TeamSet(
            teams=[
                Team(_id=1, students=students[:2]),
                Team(_id=2, students=students[2:4]),
                Team(_id=3, students=students[5:6]),
            ]
        )
        priorities = [EvenPriority(), JohnPriority()]
        priority_satisfaction = PrioritySatisfaction(
            priorities=priorities, is_linear=False
        )
        cls.students = students
        cls.team_set = team_set
        cls.priorities = priorities
        cls.priority_satisfaction = priority_satisfaction

    def test_priorities_satisfied__returns_correct_number_satisfied(self):
        priorities_satisfied = [
            self.priority_satisfaction.priorities_satisfied(team)
            for team in self.team_set.teams
        ]
        self.assertEqual([1, 1], priorities_satisfied[0])
        self.assertEqual([0, 0], priorities_satisfied[1])
        self.assertEqual([1, 0], priorities_satisfied[2])

    def test_compute_linear_weights__returns_correct_weights(self):
        weights = self.priority_satisfaction.compute_linear_weights()
        self.assertEqual([2, 1], weights)

    def test_compute_exponential_weights__returns_correct_weights(self):
        weights = self.priority_satisfaction.computer_exponential_weights()
        self.assertEqual([2 / 3, 1 / 3], weights)

    def test_calculate__evaluates_metric_correctly(self):
        actual_calculate_value = self.priority_satisfaction.calculate(self.team_set)
        self.assertAlmostEqual(5 / 3 / 3, actual_calculate_value, delta=0.000001)
        priority_satisfaction_linear = PrioritySatisfaction(
            priorities=[EvenPriority(), JohnPriority()], is_linear=True
        )
        actual_calculate_value = priority_satisfaction_linear.calculate(self.team_set)
        self.assertAlmostEqual(
            (2 + 2 + 1) / 3 / 3, actual_calculate_value, delta=0.000001
        )

    def test_standard_deviation__evaluates_metric_correctly(self):
        sd = statistics.stdev([1, 2 / 3, 0])
        calculated_value = self.priority_satisfaction.calculate_stdev(self.team_set)
        self.assertAlmostEqual(sd, calculated_value, delta=0.000001)
