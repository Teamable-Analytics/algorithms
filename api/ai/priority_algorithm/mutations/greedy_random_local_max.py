from typing import List, Dict

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet, PriorityTeam
from api.ai.priority_algorithm.mutations.utils import (
    get_available_priority_teams,
    score,
)
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.dataclasses.student import Student
import random


def greedy_local_max_mutation(
    priority_team_set: PriorityTeamSet,
    priorities: List[Priority],
    student_dict: Dict[int, Student],
):
    """
    1. Pick two random teams
    2. Pool all students of the two team together
    3. Add each student from pool back into two new pools by doing the following for each student in the pool
        - If one of the pools is full add student to not full pool, else
        - Add student to each pool and get score of each pool, keeping the student in the pool whose score increases the most
    """
    available_priority_teams: List[PriorityTeam] = get_available_priority_teams(
        priority_team_set
    )
    try:
        if len(available_priority_teams) < 2:
            return priority_team_set
        team_1, team_2 = random.sample(available_priority_teams, 2)
        team_1_size = len(team_1.student_ids)
        team_2_size = len(team_2.student_ids)
        students = team_1.student_ids + team_2.student_ids
        random.shuffle(students)
        mutated_team_1 = []
        mutated_team_2 = []
        score1 = 0
        score2 = 0
        for student in students:
            if len(mutated_team_1) >= team_1_size:
                mutated_team_2.append(student)
            elif len(mutated_team_2) >= team_2_size:
                mutated_team_1.append(student)
            else:
                # Score with student in each new pool
                team_1.student_ids = mutated_team_1 + [student]
                team_2.student_ids = mutated_team_2 + [student]
                updated_score1 = score(team_1, priorities, student_dict)
                updated_score2 = score(team_2, priorities, student_dict)

                if updated_score1 - score1 > updated_score2 - score2:
                    score1 = updated_score1
                    mutated_team_1.append(student)
                else:
                    score2 = updated_score2
                    mutated_team_2.append(student)
        team_1.student_ids = mutated_team_1
        team_2.student_ids = mutated_team_2
    except ValueError:
        return priority_team_set
    return priority_team_set
