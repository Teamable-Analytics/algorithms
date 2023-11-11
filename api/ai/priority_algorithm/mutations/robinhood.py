import itertools
import random
from typing import List, Dict, Tuple

from api.ai.priority_algorithm.priority.interfaces import Priority
from api.ai.priority_algorithm.mutations import utils
from api.ai.priority_algorithm.custom_models import PriorityTeamSet, PriorityTeam
from api.models.student import Student


ROBINHOOD_SATISFACTION_THRESHOLD = 0.8

def mutate_robinhood(
    priority_team_set: PriorityTeamSet,
    priorities: List[Priority],
    student_dict: Dict[int, Student],
) -> PriorityTeamSet:
    """
    Robinhood is a mutation that finds a team t1 that does not satisfy a priority c, and a team t2 that does satisfy c. It then creates all possible team sets by mutating the students of t1 and t2, and chooses the best team. This is done across all constraints.
    """

    # Argument checking
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
                if priority.satisfaction(
                    [student_dict[student_id] for student_id in team.student_ids]
                ) >= ROBINHOOD_SATISFACTION_THRESHOLD:
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


def mutate_robinhood_holistic(
    priority_team_set: PriorityTeamSet,
    priorities: List[Priority],
    student_dict: Dict[int, Student],
) -> PriorityTeamSet:
    """
    This is a variation of mutate_robinhood that does not consider individual priorities. Instead, it considers the entire set of priorities as a whole. This is done by calculating the score of each team in the team set, and then performing the local max portion of the robinhood mutation on the team with the lowest score and the team with the highest score.
    """

    if not valid_robinhood_arguments(priority_team_set, priorities, student_dict):
        return priority_team_set

    cloned_priority_team_set: PriorityTeamSet = priority_team_set.clone()

    available_priority_teams = [
        priority_team
        for priority_team in cloned_priority_team_set.priority_teams
        if not priority_team.team.is_locked
    ]

    # Calculate the score of each team in the team set
    team_scores: List[Tuple[PriorityTeam, int]] = []
    for team in available_priority_teams:
        team_scores.append((team, utils.score(team, priorities, student_dict)))

    # Find the min and max scores
    min_scoring_team: Tuple[PriorityTeam, int] = min(team_scores, key=lambda x: x[1])
    team_scores.remove(min_scoring_team)
    max_scoring_team: Tuple[PriorityTeam, int] = max(team_scores, key=lambda x: x[1])

    # Perform local max portion of robinhood
    team_set, score = perform_local_max_portion_of_robinhood(
        cloned_priority_team_set,
        priorities,
        student_dict,
        min_scoring_team[0],
        max_scoring_team[0],
    )

    return team_set


def perform_local_max_portion_of_robinhood(
    cloned_priority_team_set: PriorityTeamSet,
    priorities: List[Priority],
    student_dict: Dict[int, Student],
    selected_team_a: PriorityTeam,
    selected_team_b: PriorityTeam,
) -> Tuple[PriorityTeamSet, float]:
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
    students: List[int] = list(selected_team_a.student_ids) + list(
        selected_team_b.student_ids
    )

    # Generate all possible teams using the students from the two teams
    # Elements of this list are lists of student ids
    possible_teams: List[Tuple[int]] = list(
        itertools.combinations(students, len(selected_team_b.student_ids))
    )

    # Calculate the score of each team
    for team in possible_teams:
        # Modify the cloned PriorityTeamSet to reflect the new team
        selected_team_b.student_ids = list(team)
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
    if len(priority_team_set.priority_teams) < 2:
        return False
    if len(priorities) == 0:
        return False
    return True
