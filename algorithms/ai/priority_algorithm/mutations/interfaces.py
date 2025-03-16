from abc import ABC
from typing import List, Dict

from algorithms.ai.interfaces.team_generation_options import TeamGenerationOptions
from algorithms.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet
from algorithms.ai.priority_algorithm.priority.interfaces import Priority
from algorithms.dataclasses.student import Student


class Mutation(ABC):
    def __init__(self, num_mutations: int = 1):
        self.num_mutations = num_mutations

    def mutate(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
        team_generation_options: TeamGenerationOptions,
    ) -> List[PriorityTeamSet]:
        return [
            self.mutate_one(
                priority_team_set.clone(),
                priorities,
                student_dict,
                team_generation_options,
            )
            for _ in range(self.num_mutations)
        ]

    def mutate_one(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
        team_generation_options: TeamGenerationOptions,
    ) -> PriorityTeamSet:
        raise NotImplementedError
