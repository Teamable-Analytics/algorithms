import itertools
import random
from typing import List, Dict

from ai.priority_algorithm.interfaces import Priority
from ai.priority_algorithm.mutations.utils import score, get_available_teams
from ai.priority_algorithm.priority_teamset import PriorityTeamSet, PriorityTeam
from models.student import Student


def mutate_local_max(
    priority_team_set: PriorityTeamSet,
    priorities: List[Priority],
    student_dict: Dict[int, Student],
) -> PriorityTeamSet:
    """
    This mutation finds the lowest two scoring teams, and then computes the scores of all possible combinations of
    students on those teams. It replaces one of the teams with the team with the highest score found, and puts all other
    students on the other team. This implementation does not account for if the second team's score increases or
    decreases.
    """
    available_priority_teams = get_available_teams(priority_team_set)
    if len(available_priority_teams) < 2:
        return priority_team_set
    # Sort teams and take the two lowest scoring teams
    available_priority_teams = sorted(
        available_priority_teams,
        key=(lambda team: score(team, priorities, student_dict)),
    )
    team_1 = available_priority_teams[0]
    team_2 = available_priority_teams[1]
    return find_local_max(priority_team_set, priorities, student_dict, team_1, team_2)


def find_local_max(
    priority_team_set: PriorityTeamSet,
    priorities: List[Priority],
    student_dict: Dict[int, Student],
    team_1: PriorityTeam,
    team_2: PriorityTeam,
) -> PriorityTeamSet:
    # Finds all combinations of students for the two teams
    try:
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

    except ValueError:
        return priority_team_set
    return priority_team_set


def mutate_local_max_epsilon(
    priority_team_set: PriorityTeamSet,
    priorities: List[Priority],
    student_dict: Dict[int, Student],
    epsilon: float,
) -> PriorityTeamSet:
    available_priority_teams = get_available_teams(priority_team_set)
    if len(available_priority_teams) < 2:
        return priority_team_set
    # Sort teams and take the two lowest scoring teams
    chance = random.random()
    if chance < epsilon:
        team_1 = min(available_priority_teams, key=(lambda team: score(team, priorities, student_dict)))
        team_2 = team_1
        while team_1 == team_2:
            team_2 = random.choice(available_priority_teams)
    else:
        available_priority_teams = sorted(
            available_priority_teams,
            key=(lambda team: score(team, priorities, student_dict)),
        )
        team_1 = available_priority_teams[0]
        team_2 = available_priority_teams[1]
    return find_local_max(priority_team_set, priorities, student_dict, team_1, team_2)