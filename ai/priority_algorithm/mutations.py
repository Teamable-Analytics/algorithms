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
    Robinhood is a mutation that finds a team t1 that does not satisfy a priority c, and a team t2 that does satisfy c. It then creates all possible team sets by mutating the students of t1 and t2, and chooses the best team. This is done across all constraints.
    """

    # Argument checking
    # Can also raise a ValueError
    if not valid_robinhood_arguments(priority_team_set, priorities, student_dict):
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

            # Perform the local max portion of the robinhood mutation
            (
                local_best_team_set,
                local_best_team_set_score,
            ) = perform_local_max_portion_of_robinhood(
                cloned_priority_team_set,
                priorities,
                student_dict,
                satisfied_team,
                unsatisfied_team,
            )

            # Update the best team set if the local best team set is better
            if local_best_team_set_score > best_team_set_score:
                best_team_set = local_best_team_set
                best_team_set_score = local_best_team_set_score
    except ValueError:
        return best_team_set
    return best_team_set


def perform_local_max_portion_of_robinhood(
    cloned_priority_team_set: PriorityTeamSet,
    priorities: List[Priority],
    student_dict: Dict[int, Student],
    selected_team_a: PriorityTeam,
    selected_team_b: PriorityTeam,
) -> (PriorityTeamSet, float):
    """
    Performs the local max portion of the robinhood mutation. This is the part where we generate all possible teams using the students from the two teams, and choose the best team.

    returns (best_team_set, best_team_set_score)
    """

    # Init best team set
    best_team_set: PriorityTeamSet = cloned_priority_team_set
    best_team_set_score: float = cloned_priority_team_set.calculate_score(
        priorities, student_dict
    )

    # List of all students in the two teams
    students: List[int] = selected_team_a.student_ids + selected_team_b.student_ids

    # Generate all possible teams using the students from the two teams
    # Elements of this list are lists of student ids
    possible_teams: List[List[int]] = list(
        itertools.combinations(students, len(selected_team_b.student_ids))
    )

    # Calculate the score of each team
    for team in possible_teams:
        # Modify the cloned PriorityTeamSet to reflect the new team
        selected_team_b.student_ids = team
        selected_team_a.student_ids = [
            student_id for student_id in students if student_id not in team
        ]

        # Calculate the score of the resulting PriorityTeamSet
        cloned_priority_team_set.score = (
            None  # Reset the score to force recalculation after modification
        )
        score = cloned_priority_team_set.calculate_score(priorities, student_dict)
        if score > best_team_set_score:
            # Clone the PriorityTeamSet because we will be modifying on the next iteration
            best_team_set = cloned_priority_team_set.clone()
            best_team_set_score = score

    return best_team_set, best_team_set_score


def valid_robinhood_arguments(
    priority_team_set: PriorityTeamSet,
    priorities: List[Priority],
    student_dict: Dict[int, Student],
) -> bool:
    if len(priority_team_set.priority_teams) == 0:
        raise ValueError("PriorityTeamSet must have at least one team")
    if len(priority_team_set.priority_teams) == 1:
        return False
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
        return False
    return True


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
