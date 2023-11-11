import unittest
from typing import List

from api.ai.new.priority_algorithm.priority.priority import TokenizationPriority, DiversityPriority
from api.models.enums import (
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
)
from api.models.tokenization_constraint import TokenizationConstraint
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Goal
from benchmarking.simulation.goal_to_priority import (
    goal_to_priority,
)


class TestGoalToPriority(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.goals: List[Goal] = [
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.GPA.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MAX_OF,
                    threshold=2,
                    value=1,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.AGE.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=3,
                    value=2,
                ),
            ),
            DiversityGoal(DiversifyType.DIVERSIFY, ScenarioAttribute.MAJOR.value),
            WeightGoal(diversity_goal_weight=1),
        ]

    def test_goal_to_priority__converts_goal_into_priority_correctly(self):
        priority_1 = goal_to_priority(self.goals[0])
        expected_priority_1 = TokenizationPriority(
            attribute_id=ScenarioAttribute.GPA.value,
            strategy=DiversifyType.CONCENTRATE,
            direction=TokenizationConstraintDirection.MAX_OF,
            threshold=2,
            value=1,
        )
        self.assertEqual(expected_priority_1, priority_1)
        priority_2 = goal_to_priority(self.goals[1])
        expected_priority_2 = TokenizationPriority(
            attribute_id=ScenarioAttribute.AGE.value,
            strategy=DiversifyType.DIVERSIFY,
            direction=TokenizationConstraintDirection.MIN_OF,
            threshold=3,
            value=2,
        )
        self.assertEqual(expected_priority_2, priority_2)

        priority_3 = goal_to_priority(self.goals[2])
        expected_priority_3 = DiversityPriority(
            attribute_id=ScenarioAttribute.MAJOR.value,
            strategy=DiversifyType.DIVERSIFY,
        )
        self.assertEqual(expected_priority_3, priority_3)

        self.assertRaises(NotImplementedError, goal_to_priority, self.goals[3])
