from abc import ABC
from typing import List, Dict

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
