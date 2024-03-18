from abc import ABC
from typing import List, Dict, Tuple

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.dataclasses.student import Student


class Mutation(ABC):
    def mutate(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
    ):
        raise NotImplementedError


class MutationSet:
    def __init__(self, mutations: List[Tuple[Mutation, int]]):
        """
        A set of mutations to be run in a single iteration of the priority algorithm.

        Parameters
        ----------
        mutations - A list of tuples of a Mutation to the number of times it should be called.
        """
        self.mutations = mutations

    def generate_mutations(
        self,
        team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
    ) -> List[PriorityTeamSet]:
        mutated_team_sets: List[PriorityTeamSet] = []
        for mutation, num_calls in self.mutations:
            mutated_team_sets.extend(
                [
                    mutation.mutate(
                        team_set.clone(),
                        priorities,
                        student_dict,
                    )
                    for _ in range(num_calls)
                ]
            )
        return mutated_team_sets

    def sum_of_calls(self) -> int:
        return sum([num_calls for mutation, num_calls in self.mutations])
