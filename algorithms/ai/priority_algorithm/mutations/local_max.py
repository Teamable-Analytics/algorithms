from typing import List, Dict

from algorithms.ai.interfaces.team_generation_options import TeamGenerationOptions
from algorithms.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet
from algorithms.ai.priority_algorithm.mutations.interfaces import Mutation
from algorithms.ai.priority_algorithm.mutations.utils import (
    score,
    get_available_priority_teams,
    local_max,
)
from algorithms.ai.priority_algorithm.priority.interfaces import Priority
from algorithms.dataclasses.student import Student


class LocalMaxMutation(Mutation):
    def mutate_one(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
        team_generation_options: TeamGenerationOptions,
    ) -> PriorityTeamSet:
        """
        This mutation finds the lowest two scoring teams, and then computes the scores of all possible combinations of
        students on those teams. It replaces one of the teams with the team with the highest score found, and puts all other
        students on the other team. This implementation does not account for if the second team's score increases or
        decreases.
        """
        available_priority_teams = get_available_priority_teams(priority_team_set)
        try:
            if len(available_priority_teams) < 2:
                return priority_team_set
            # Sort teams and take the two lowest scoring teams
            available_priority_teams = sorted(
                available_priority_teams,
                key=(lambda team: score(team, priorities, student_dict)),
            )
            team_1 = available_priority_teams[0]
            team_2 = available_priority_teams[1]
            local_max(team_1, team_2, priorities, student_dict)

        except ValueError:
            return priority_team_set
        return priority_team_set
