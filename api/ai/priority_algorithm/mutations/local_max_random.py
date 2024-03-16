import random
from typing import List, Dict

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet
from api.ai.priority_algorithm.mutations.mutation import Mutation
from api.ai.priority_algorithm.mutations.utils import (
    get_available_priority_teams,
    score,
    local_max,
)
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.dataclasses.student import Student


class LocalMaxRandomMutation(Mutation):
    def mutate(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
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
            # Sort teams and take the two lowest scoring teams
            team_1 = min(
                available_priority_teams,
                key=(lambda team: score(team, priorities, student_dict)),
            )
            team_2 = team_1
            while team_2 == team_1:
                team_2 = random.sample(available_priority_teams, 1)[0]
            local_max(team_1, team_2, priorities, student_dict)

        except ValueError:
            return priority_team_set
        return priority_team_set
