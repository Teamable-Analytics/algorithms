from abc import ABC
from typing import List, Dict, Tuple

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.dataclasses.student import Student


class Mutation(ABC):
    def __init__(self, num_mutations: int = 1):
        self._num_mutations = num_mutations

    def mutate(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
    ) -> List[PriorityTeamSet]:
        return [
            self.mutate_one(
                priority_team_set.clone(),
                priorities,
                student_dict,
            )
            for _ in range(self._num_mutations)
        ]

    def mutate_one(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
    ) -> PriorityTeamSet:
        raise NotImplementedError

    def num_mutations(self) -> int:
        return self._num_mutations


class MutationSet:
    def __init__(self, mutations: List[Mutation]):
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
        for mutation in self.mutations:
            mutated_team_sets.extend(
                mutation.mutate(
                    team_set,
                    priorities,
                    student_dict,
                )
            )
        return mutated_team_sets

    def sum_of_calls(self) -> int:
        return sum([mutation.num_mutations() for mutation in self.mutations])
