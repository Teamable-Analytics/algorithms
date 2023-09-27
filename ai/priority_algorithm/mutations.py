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


def mutate_robinhood(
    priority_team_set: PriorityTeamSet,
    priorities: List[Priority],
    student_dict: Dict[int, Student],
) -> PriorityTeamSet:
    """
    Robinhood is a mutation that finds a team t1 that does not satisfy a priority c, and a team t2 that does satisfy c.
    It then creates all possible teams using the students of t1 and t2, and chooses the M best teams.
    """

    # Argument checking
    if len(priority_team_set.priority_teams) == 0:
        raise ValueError("PriorityTeamSet must have at least one team")
    if len(priority_team_set.priority_teams) == 1:
        return priority_team_set
    if len(priorities) == 0:
        raise ValueError("Must have at least one priority")
    all_students: List[Student] = [
        student
        for team in priority_team_set.priority_teams
        for student in team.team.students
    ]
    if len(all_students) != len(student_dict):
        raise ValueError("student_dict must contain all students in priority_team_set")
    for student in all_students:
        if student.id not in student_dict:
            raise ValueError(
                "student_dict must contain all students in priority_team_set"
            )
    if len(all_students) == 0:
        raise ValueError("PriorityTeamSet must have at least one student")
    if (
        len(
            [
                team
                for team in priority_team_set.priority_teams
                if not team.team.is_locked
            ]
        )
        < 2
    ):
        return priority_team_set

    # Init best team set
    best_team_set: PriorityTeamSet = priority_team_set
    best_team_set_score: float = priority_team_set.calculate_score(
        priorities, student_dict
    )
    try:
        for priority in priorities:
            # We need to clone the priority_team_set because we will be modifying it in order to get the score of the whole TeamSet
            cloned_priority_team_set: PriorityTeamSet = priority_team_set.clone()

            available_priority_teams = [
                priority_team
                for priority_team in cloned_priority_team_set.priority_teams
                if not priority_team.team.is_locked
            ]

            # Sort the teams into two lists: those that satisfy the priority and those that don't
            satisfied_teams: List[PriorityTeam] = []
            unsatisfied_teams: List[PriorityTeam] = []
            for team in available_priority_teams:
                if priority.satisfied_by(
                    [student_dict[student_id] for student_id in team.student_ids]
                ):
                    satisfied_teams.append(team)
                else:
                    unsatisfied_teams.append(team)

            # Choose a random team from each list
            if len(unsatisfied_teams) == 0 or len(satisfied_teams) == 0:
                satisfied_team = random.choice(available_priority_teams)
                unsatisfied_team = random.choice(
                    [
                        team
                        for team in available_priority_teams
                        if team != satisfied_team
                    ]
                )
            else:
                satisfied_team = random.choice(satisfied_teams)
                unsatisfied_team = random.choice(unsatisfied_teams)

            # List of all students in the two teams
            students: List[int] = (
                satisfied_team.student_ids + unsatisfied_team.student_ids
            )

            # Generate all possible teams using the students from the two teams
            # Elements of this list are lists of student ids
            possible_teams: List[List[int]] = list(
                itertools.combinations(students, len(unsatisfied_team.student_ids))
            )

            # Calculate the score of each team
            for team in possible_teams:
                # Modify the cloned PriorityTeamSet to reflect the new team
                unsatisfied_team.student_ids = team
                satisfied_team.student_ids = [
                    student_id for student_id in students if student_id not in team
                ]

                # Calculate the score of the resulting PriorityTeamSet
                cloned_priority_team_set.score = (
                    None  # Reset the score to force recalculation after modification
                )
                score = cloned_priority_team_set.calculate_score(
                    priorities, student_dict
                )
                if score > best_team_set_score:
                    # Clone the PriorityTeamSet because we will be modifying on the next iteration
                    best_team_set = cloned_priority_team_set.clone()
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
