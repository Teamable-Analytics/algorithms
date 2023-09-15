from math import floor
from typing import List, Dict, TYPE_CHECKING

from ai.priority_algorithm.interfaces import Priority
from models.student import Student

if TYPE_CHECKING:
    from ai.priority_algorithm.priority_teamset import PriorityTeam

NUM_BUCKETS = 25


def get_priority_satisfaction_array(
    priority_teams: List["PriorityTeam"],
    priorities: List[Priority],
    student_dict: Dict[int, Student],
) -> List[int]:
    return [
        get_priority_satisfaction(priority_teams, priority, student_dict)
        for priority in priorities
    ]


def get_priority_satisfaction(
    priority_teams: List["PriorityTeam"],
    priority: Priority,
    student_dict: Dict[int, Student],
) -> int:
    satisfaction_ratio = get_satisfaction_ratio(priority_teams, priority, student_dict)
    if satisfaction_ratio == 0:
        return 0
    if satisfaction_ratio == 1:
        return NUM_BUCKETS - 1

    return min(floor(satisfaction_ratio * NUM_BUCKETS), NUM_BUCKETS - 1)


def get_satisfaction_ratio(
    priority_teams: List["PriorityTeam"],
    priority: Priority,
    student_dict: Dict[int, Student],
) -> float:
    # returns value in [0, 1] IMPORTANT that it does this, satisfaction value relies on it
    count = 0
    for priority_team in priority_teams:
        count += priority.satisfied_by(
            [student_dict[student_id] for student_id in priority_team.student_ids]
        )
    return count / len(priority_teams)


def get_multipliers(priorities: List[Priority]) -> List[int]:
    # with 2 buckets and [C1, C2, C3], returns [4, 2, 1]
    multipliers = [NUM_BUCKETS ** (n - 1) for n in range(1, len(priorities) + 1)]
    return multipliers[::-1]
