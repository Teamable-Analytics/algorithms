import random
from typing import List, Dict

from algorithms.ai.interfaces.team_generation_options import TeamGenerationOptions
from algorithms.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet
from algorithms.ai.priority_algorithm.mutations.interfaces import Mutation
from algorithms.ai.priority_algorithm.mutations.utils import (
    get_available_priority_teams,
    local_max,
)
from algorithms.ai.priority_algorithm.priority.interfaces import Priority
from algorithms.dataclasses.student import Student


class LocalMaxDoubleRandomMutation(Mutation):
    def mutate_one(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
        team_generation_options: TeamGenerationOptions,
    ) -> PriorityTeamSet:
        """
        This mutation finds the lowest scoring team and one random team, and then computes the scores of all possible
        combinations of students on those teams. It replaces one of the teams with the team with the highest score found,
        and puts all other students on the other team. This implementation does not account for if the second team's score
        increases or decreases.
        """
        available_priority_teams = get_available_priority_teams(priority_team_set)
        try:
            if len(available_priority_teams) < 2:
                return priority_team_set
            team_1, team_2 = random.sample(available_priority_teams, 2)
            local_max(team_1, team_2, priorities, student_dict)

        except ValueError:
            return priority_team_set
        return priority_team_set
