import random
from typing import Dict, List

from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet
from api.ai.priority_algorithm.mutations.interfaces import Mutation
from api.ai.priority_algorithm.mutations.utils import get_available_priority_teams
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.dataclasses.student import Student


class RandomTeamSizeMutation(Mutation):
    def __init__(self, num_mutations: int = 1, number_of_teams: int = 2):
        super().__init__(num_mutations)
        self.number_of_teams = number_of_teams

    def validate(self):
        if self.number_of_teams < 2:
            raise ValueError("Random team size mutation must have at least two teams")

    def mutate_one(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
        team_generation_options: TeamGenerationOptions,
    ) -> PriorityTeamSet:
        if (
            team_generation_options.max_team_size
            - team_generation_options.min_team_size
            < 2
        ):
            print(
                "Warning: There is little to no effect if there is not at least a gap of two between the min and max team sizes."
            )
        try:
            available_priority_teams = get_available_priority_teams(priority_team_set)
            if len(available_priority_teams) < self.number_of_teams:
                return priority_team_set
            teams = random.sample(available_priority_teams, self.number_of_teams)
            students = [
                student_id
                for team in teams
                for student_id in team.student_ids[
                    team_generation_options.min_team_size :
                ]
            ]
            for team in teams:
                team.student_ids = team.student_ids[
                    : team_generation_options.min_team_size
                ]
            random.shuffle(students)
            for student in students:
                index = random.randrange(0, self.number_of_teams)
                for i in range(self.number_of_teams):
                    j = (index + i) % self.number_of_teams
                    if (
                        len(teams[j].student_ids)
                        < team_generation_options.max_team_size
                    ):
                        teams[j].student_ids.append(student)
                        break
        except ValueError:
            return priority_team_set
        return priority_team_set
