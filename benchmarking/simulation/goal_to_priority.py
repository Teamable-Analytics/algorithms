from typing import List, Literal

from api.ai.priority_algorithm.interfaces import Priority
from api.ai.priority_algorithm.priority import TokenizationPriority
from benchmarking.evaluations.goals import DiversityGoal
from benchmarking.evaluations.interfaces import Goal


def goals_to_priorities(goals: List[Goal]) -> List[Priority]:
    return [goal_to_priority(goal) for goal in goals]


def goal_to_priority(goal: Goal) -> Priority:
    if not isinstance(goal, DiversityGoal):
        raise NotImplementedError
    if goal.tokenization_constraint is None:
        raise NotImplementedError

    return TokenizationPriority(
        attribute_id=goal.attribute,
        strategy=goal.strategy,
        direction=goal.tokenization_constraint.direction,
        threshold=goal.tokenization_constraint.threshold,
        value=goal.tokenization_constraint.value,
    )
