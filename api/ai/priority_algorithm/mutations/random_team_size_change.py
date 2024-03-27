from typing import Dict, List

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet
from api.ai.priority_algorithm.mutations.interfaces import Mutation
from api.ai.priority_algorithm.mutations.utils import get_available_priority_teams
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.dataclasses.student import Student


class RandomTeamSizeMutation(Mutation):
    def __init__(self, number_of_teams: int = 2):
        super().__init__()
        self.number_of_teams = number_of_teams

    def validate(self):
        if self.number_of_teams < 2:
            raise ValueError("Random team size mutation must have at least two teams")


    def mutate_one(
            self,
            priority_team_set: PriorityTeamSet,
            priorities: List[Priority],
            student_dict: Dict[int, Student],
            min_team_size: int,
            max_team_size: int,
    ) -> PriorityTeamSet:
        try:
            available_priority_teams = get_available_priority_teams(priority_team_set)

        except ValueError:
            return priority_team_set
        return priority_team_set

