from typing import List

from api.ai.priority_algorithm.priority.interfaces import Priority
from api.ai.priority_algorithm.priority.priority import (
    DiversityPriority,
    TokenizationPriority,
    RequirementPriority,
)
from benchmarking.evaluations.goals import DiversityGoal, ProjectRequirementGoal
from benchmarking.evaluations.interfaces import Goal


def goals_to_priorities(goals: List[Goal]) -> List[Priority]:
    priorities = []
    for goal in goals:
        try:
            priorities.append(goal_to_priority(goal))
        except NotImplementedError:
            continue
    return priorities


def goal_to_priority(goal: Goal) -> Priority:
    if isinstance(goal, ProjectRequirementGoal) and goal.match_skills:
        return RequirementPriority(
            criteria=goal.criteria,
        )

    if isinstance(goal, DiversityGoal):
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

    raise NotImplementedError
