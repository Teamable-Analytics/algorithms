import itertools
import random
from typing import List, Dict

from ai.priority_algorithm.interfaces import Priority
from ai.priority_algorithm.priority_teamset import PriorityTeamSet, PriorityTeam
from ai.priority_algorithm.scoring import get_priority_satisfaction_array, get_multipliers
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


def mutate_robinhood(
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
) -> PriorityTeamSet:
    """
    Robinhood is a mutation that finds a team t1 that does not satisfy a priority c, and a team t2 that does satisfy c.
    It then creates all possible teams using the students of t1 and t2, and chooses the M best teams.
    """
    best_team_set: PriorityTeamSet = priority_team_set
    best_team_set_score: float = priority_team_set.calculate_score(priorities, student_dict)
    try:
        for priority in priorities:
            cloned_priority_team_set: PriorityTeamSet = priority_team_set.clone()
            available_priority_teams = [
                priority_team
                for priority_team in cloned_priority_team_set.priority_teams
                if not priority_team.team.is_locked
            ]

            # Get all teams that satisfy the priority
            satisfied_teams: List[PriorityTeam] = [
                team for team in available_priority_teams if priority.satisfied_by(
                    [student_dict[student_id] for student_id in team.student_ids]
                )
            ]
            # Get all teams that do not satisfy the priority
            unsatisfied_teams: List[PriorityTeam] = [
                team for team in available_priority_teams if team not in satisfied_teams
            ]

            # Choose a random team from each list
            satisfied_team: PriorityTeam = satisfied_teams.pop(random.randrange(len(satisfied_teams)))
            unsatisfied_team: PriorityTeam = unsatisfied_teams.pop(random.randrange(len(unsatisfied_teams)))

            # List of all students in the two teams
            students: List[int] = satisfied_team.student_ids + unsatisfied_team.student_ids

            # Generate all possible teams using the students from the two teams
            # Elements of this list are lists of student ids
            possible_teams: List[List[int]] = list(itertools.combinations(students, len(unsatisfied_team.student_ids)))

            # Find the Calculate the score of each team
            for team in possible_teams:
                # Build teams
                team_1 = unsatisfied_team
                team_1.student_ids = team
                team_2 = satisfied_team
                team_2.student_ids = [student_id for student_id in students if student_id not in team]

                # Build the resulting PriorityTeamSet
                cloned_priority_team_set.priority_teams = [
                    *[
                        team for team in cloned_priority_team_set.priority_teams if team not in [team_1, team_2]
                    ],
                    team_1,
                    team_2
                ]

                # Calculate the score of the resulting PriorityTeamSet
                score = cloned_priority_team_set.calculate_score(priorities, student_dict)
                if score > best_team_set_score:
                    best_team_set = cloned_priority_team_set
                    best_team_set_score = score
    except ValueError:
        return best_team_set
    return best_team_set


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
