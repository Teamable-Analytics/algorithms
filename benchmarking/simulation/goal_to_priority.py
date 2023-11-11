from typing import List

from api.ai.new.priority_algorithm.priority.interfaces import Priority
from api.ai.new.priority_algorithm.priority.priority import DiversityPriority, TokenizationPriority
from benchmarking.evaluations.goals import DiversityGoal
from benchmarking.evaluations.interfaces import Goal


def goals_to_priorities(goals: List[Goal]) -> List[Priority]:
    return [goal_to_priority(goal) for goal in goals]


def goal_to_priority(goal: Goal) -> Priority:
    if not isinstance(goal, DiversityGoal):
        raise NotImplementedError

    if goal.tokenization_constraint is None:
        return DiversityPriority(
            attribute_id=goal.attribute,
            strategy=goal.strategy,
        )

    return TokenizationPriority(
        attribute_id=goal.attribute,
        strategy=goal.strategy,
        direction=goal.tokenization_constraint.direction,
        threshold=goal.tokenization_constraint.threshold,
        value=goal.tokenization_constraint.value,
    )
