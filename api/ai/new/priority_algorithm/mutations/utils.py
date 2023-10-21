from typing import List, Dict

from api.ai.new.priority_algorithm.priority.interfaces import Priority
from api.ai.new.priority_algorithm.custom_models import PriorityTeam
from api.ai.new.priority_algorithm.scoring import (
    get_multipliers,
    get_priority_satisfaction_array,
)
from api.models.student import Student


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
