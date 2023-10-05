from typing import List, Literal

from api.ai.priority_algorithm.interfaces import Priority
from api.ai.priority_algorithm.priority import TokenizationPriority
from api.models.enums import DiversifyType, TokenizationConstraintDirection
from benchmarking.evaluations.goals import DiversityGoal
from benchmarking.evaluations.interfaces import Goal
from benchmarking.simulation.algorithm_translator import AlgorithmTranslator


def get_strategy(constraint: Literal["diversify", "concentrate"]):
    if constraint == "diversify":
        return DiversifyType.DIVERSIFY
    if constraint == "concentrate":
        return DiversifyType.CONCENTRATE
    raise TypeError


def get_direction(limit_option: Literal["min_of", "max_of"]):
    if limit_option == "min_of":
        return TokenizationConstraintDirection.MIN_OF
    if limit_option == "max_of":
        return TokenizationConstraintDirection.MAX_OF
    raise TypeError


def goals_to_priorities(goals: List[Goal]) -> List[Priority]:
    return [goal_to_priority(goal) for goal in goals]


def goal_to_priority(goal: Goal) -> Priority:
    if not isinstance(goal, DiversityGoal):
        raise NotImplementedError
    priority = AlgorithmTranslator.diversity_goal_to_algorithm_priority_dict(goal)

    return TokenizationPriority(
        attribute_id=priority["skill_id"],
        strategy=get_strategy(priority["constraint"]),
        direction=get_direction(priority["limit_option"]),
        threshold=priority["limit"],
        value=priority["value"],
    )
