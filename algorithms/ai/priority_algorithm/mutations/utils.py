import itertools
from typing import List, Dict

from algorithms.ai.priority_algorithm.priority.interfaces import Priority
from algorithms.ai.priority_algorithm.custom_dataclasses import (
    PriorityTeam,
    PriorityTeamSet,
)
from algorithms.ai.priority_algorithm.scoring import (
    get_multipliers,
    get_priority_satisfaction_array,
)
from algorithms.dataclasses.student import Student


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
        if not priority_team.team_shell.is_locked
    ]


def local_max(
    team_1: PriorityTeam,
    team_2: PriorityTeam,
    priorities: List[Priority],
    student_dict: Dict[int, Student],
):
    # Finds all combinations of students for the two teams
    students = team_1.student_ids + team_2.student_ids
    # TODO: Determine how we want to find team size
    team_size = len(team_1.student_ids)
    student_combinations = list(itertools.combinations(students, team_size))

    max_score = 0
    max_index = 0
    for i, combo in enumerate(student_combinations):
        combo_1 = [
            *combo,
        ]
        combo_2 = [_ for _ in students if _ not in combo_1]
        team_1.student_ids = combo_1
        team_2.student_ids = combo_2
        team_1_score = score(team_1, priorities, student_dict)
        team_2_score = score(team_2, priorities, student_dict)
        if team_1_score > max_score or team_2_score > max_score:
            max_index = i
            max_score = max(team_1_score, team_2_score)

    best_team_1_students = [
        *student_combinations[max_index],
    ]
    best_team_2_students = [_ for _ in students if _ not in best_team_1_students]
    team_1.student_ids = best_team_1_students
    team_2.student_ids = best_team_2_students
