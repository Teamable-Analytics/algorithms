import random
from random import shuffle
from typing import List, Dict

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet
from api.ai.priority_algorithm.mutations.interfaces import Mutation
from api.ai.priority_algorithm.mutations.utils import get_available_priority_teams
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.dataclasses.student import Student


class RandomSliceMutation(Mutation):
    def mutate(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
    ):
        """
        This mutation takes one student from each team and swaps them
        """
        available_priority_teams = get_available_priority_teams(priority_team_set)
        try:
            if len(available_priority_teams) < 2:
                return priority_team_set

            # Pop a random student from each team
            picked_students = []
            for team in available_priority_teams:
                picked_students.append(
                    team.student_ids.pop(random.randrange(len(team.student_ids)))
                )

            # Shuffle picked students
            shuffle(picked_students)

            # Put them back into the teams
            for team in available_priority_teams:
                team.student_ids.append(picked_students.pop())

        except ValueError:
            return priority_team_set
        return priority_team_set
