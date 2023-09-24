import itertools
import random
from typing import List, Dict

from ai.priority_algorithm.interfaces import Priority
from ai.priority_algorithm.priority_teamset import PriorityTeamSet, PriorityTeam
from ai.priority_algorithm.scoring import (
    get_priority_satisfaction_array,
    get_multipliers,
)
from models.student import Student


def swap_student_between_teams(
    team_1: PriorityTeam,
    student_1_id: int,
    team_2: PriorityTeam,
    student_2_id: int,
):
    team_1.student_ids.remove(student_1_id)
    team_1.student_ids.append(student_2_id)

    team_2.student_ids.remove(student_2_id)
    team_2.student_ids.append(student_1_id)


def mutate_random_swap(priority_team_set: PriorityTeamSet) -> PriorityTeamSet:
    available_priority_teams = [
        priority_team
        for priority_team in priority_team_set.priority_teams
        if not priority_team.team.is_locked
    ]
    try:
        team_1, team_2 = random.sample(available_priority_teams, 2)
        student_1_id: int = random.choice(team_1.student_ids)
        student_2_id: int = random.choice(team_2.student_ids)
        swap_student_between_teams(team_1, student_1_id, team_2, student_2_id)
    except ValueError:
        return priority_team_set
    return priority_team_set


def mutate_local_max(
    priority_team_set: PriorityTeamSet,
    priorities: List[Priority],
    student_dict: Dict[int, Student],
) -> PriorityTeamSet:
    available_priority_teams = [
        priority_team
        for priority_team in priority_team_set.priority_teams
        if not priority_team.team.is_locked
    ]
    try:
        # Sort teams and take the two lowest scoring teams
        available_priority_teams = sorted(
            available_priority_teams,
            key=(lambda team: score(team, priorities, student_dict)),
        )
        team_1 = available_priority_teams[0]
        team_2 = available_priority_teams[1]

        # Finds all combinations of students for the two teams
        students = team_1.student_ids + team_2.student_ids
        # TODO: Determine how we want to find team size
        team_size = len(team_1.student_ids)
        student_combinations = list(itertools.combinations(students, team_size))

        # Make into team_sets


    except ValueError:
        return priority_team_set
    return priority_team_set


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
