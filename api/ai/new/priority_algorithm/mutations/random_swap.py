import random

from api.ai.new.priority_algorithm.custom_models import PriorityTeamSet, PriorityTeam
from api.ai.new.priority_algorithm.mutations.utils import get_available_priority_teams


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


def mutate_random_swap(
    priority_team_set: PriorityTeamSet, *args, **kwargs
) -> PriorityTeamSet:
    available_priority_teams = get_available_priority_teams(priority_team_set)
    try:
        team_1, team_2 = random.sample(available_priority_teams, 2)
        student_1_id: int = random.choice(team_1.student_ids)
        student_2_id: int = random.choice(team_2.student_ids)
        swap_student_between_teams(team_1, student_1_id, team_2, student_2_id)
    except ValueError:
        return priority_team_set
    return priority_team_set
