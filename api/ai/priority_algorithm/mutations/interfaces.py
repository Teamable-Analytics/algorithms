from abc import ABC
from typing import List, Dict, Tuple

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.dataclasses.student import Student


class Mutation(ABC):
    def __init__(self, num_mutations: int = 1):
        self.num_mutations = num_mutations

    def mutate(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
        min_team_size: int,
        max_team_size: int,
    ) -> List[PriorityTeamSet]:
        return [
            self.mutate_one(
                priority_team_set.clone(),
                priorities,
                student_dict,
                min_team_size,
                max_team_size,
            )
            for _ in range(self.num_mutations)
        ]

    def mutate_one(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
        min_team_size: int,
        max_team_size: int,
    ) -> PriorityTeamSet:
        raise NotImplementedError
