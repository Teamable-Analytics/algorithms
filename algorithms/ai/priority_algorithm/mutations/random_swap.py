import random
from typing import List, Dict

from algorithms.ai.interfaces.team_generation_options import TeamGenerationOptions
from algorithms.ai.priority_algorithm.custom_dataclasses import (
    PriorityTeamSet,
    PriorityTeam,
)
from algorithms.ai.priority_algorithm.mutations.interfaces import Mutation
from algorithms.ai.priority_algorithm.mutations.utils import (
    get_available_priority_teams,
)
from algorithms.ai.priority_algorithm.priority.interfaces import Priority
from algorithms.dataclasses.student import Student


class RandomSwapMutation(Mutation):
    def mutate_one(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
        team_generation_options: TeamGenerationOptions,
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
