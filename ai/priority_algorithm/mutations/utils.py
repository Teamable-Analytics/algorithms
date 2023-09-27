from typing import List, Dict

from ai.priority_algorithm.interfaces import Priority
from ai.priority_algorithm.priority_teamset import PriorityTeam
from ai.priority_algorithm.scoring import (
    get_priority_satisfaction_array,
    get_multipliers,
)
from models.student import Student


def score(
    priority_team: PriorityTeam,
    priorities: List[Priority],
    student_dict: Dict[int, Student],
) -> int:
    priority_satisfaction_array = get_priority_satisfaction_array(
        [priority_team], priorities, student_dict
    )
    multipliers = get_multipliers(priorities)
    return sum(
        [
            satisfaction * multiplier
            for satisfaction, multiplier in zip(
                priority_satisfaction_array, multipliers
            )
        ]
    )
