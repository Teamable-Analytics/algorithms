from typing import List, Dict

from api.ai.priority_algorithm.priority.interfaces import Priority
from api.ai.priority_algorithm.custom_models import PriorityTeam, PriorityTeamSet
from api.ai.priority_algorithm.scoring import (
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


def get_available_priority_teams(
    priority_team_set: PriorityTeamSet,
) -> List[PriorityTeam]:
    return [
        priority_team
        for priority_team in priority_team_set.priority_teams
        if not priority_team.team.is_locked
    ]
