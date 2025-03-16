from typing import List

from algorithms.ai.priority_algorithm.priority.interfaces import Priority
from algorithms.ai.priority_algorithm.priority.priority import (
    DiversityPriority,
    TokenizationPriority,
    RequirementPriority,
    ProjectPreferencePriority,
    SocialPreferencePriority,
)
from algorithms.dataclasses.enums import PreferenceSubject
from benchmarking.evaluations.goals import (
    DiversityGoal,
    ProjectRequirementGoal,
    PreferenceGoal,
)
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
    if isinstance(goal, PreferenceGoal):
        if goal.subject == PreferenceSubject.PROJECTS:
            return ProjectPreferencePriority(
                max_project_preferences=goal.max_project_preferences,
                direction=goal.direction,
            )
        if goal.subject in [PreferenceSubject.FRIENDS, PreferenceSubject.ENEMIES]:
            return SocialPreferencePriority(
                max_num_friends=goal.max_num_friends,
                max_num_enemies=goal.max_num_enemies,
            )

    if isinstance(goal, ProjectRequirementGoal):
        return RequirementPriority()

    if isinstance(goal, DiversityGoal):
        if goal.tokenization_constraint is None:
            return DiversityPriority(
                attribute_id=goal.attribute,
                strategy=goal.strategy,
                max_num_choices=goal.max_num_choices,
            )

        return TokenizationPriority(
            attribute_id=goal.attribute,
            strategy=goal.strategy,
            direction=goal.tokenization_constraint.direction,
            threshold=goal.tokenization_constraint.threshold,
            value=goal.tokenization_constraint.value,
        )

    raise NotImplementedError
