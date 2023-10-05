from typing import List

from ai.priority_algorithm.interfaces import Priority
from benchmarking.evaluations.interfaces import Goal


def goals_to_priorities(goals: List[Goal]) -> List[Priority]:
    pass

def goal_to_priority(goal: Goal) -> Priority:
    AlgorithmTranslator.diversity_goal_to_algorithm_priority_dict(goal)
    priorities.append(
        # todo: currently, only tokenization priorities are supported
        TokenizationPriority(
            attribute_id=priority["skill_id"],
            strategy=get_strategy(priority["constraint"]),
            direction=get_direction(priority["limit_option"]),
            threshold=priority["limit"],
            value=priority["value"],
        )
    )
    pass

