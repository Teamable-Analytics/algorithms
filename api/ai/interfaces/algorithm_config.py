from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, List

from api.ai.priority_algorithm.mutations.interfaces import Mutation
from api.ai.priority_algorithm.mutations.random_swap import RandomSwapMutation
from api.dataclasses.student import Student
from api.dataclasses.team import TeamShell


@dataclass
class AlgorithmConfig(ABC):
    """
    An algorithm config is semantically different from AlgorithmOptions.
    AlgorithmConfig specifies underlying constants and internals that are largely set by developers, not the user.

    i.e. The maximum amount of time an algorithm is allowed to run for is a config choice, not an options choice.
    """

    name: str = None

    def __post_init__(self):
        self.validate()
        if self.name == "default":
            raise ValueError(
                "The name default is reserved for the default configuration"
            )
        self.name = self.name or "default"

    @abstractmethod
    def validate(self):
        pass


class RandomAlgorithmConfig(AlgorithmConfig):
    def validate(self):
        super().validate()


class WeightAlgorithmConfig(AlgorithmConfig):
    def validate(self):
        super().validate()


class SocialAlgorithmConfig(AlgorithmConfig):
    def validate(self):
        super().validate()


class PriorityAlgorithmStartType(Enum):
    RANDOM = "random"
    WEIGHT = "weight"


@dataclass
class PriorityAlgorithmConfig(AlgorithmConfig):
    MAX_KEEP: int = 3  # nodes
    MAX_SPREAD: int = 3  # nodes
    MAX_ITERATE: int = 1500  # iterations
    MAX_TIME: int = 30  # seconds
    START_TYPE: PriorityAlgorithmStartType = PriorityAlgorithmStartType.WEIGHT

    """
    Specifies the mutations as a list of [mutation_function, number_team_sets_generated_this_way]
    i.e. if one wants to mutate by "make 3 team sets using random mutation and 5 using local max mutation":
        [
            (random_mutation, 3),
            (local_max_mutation, 5),
        ]
    """
    MUTATIONS: List[Mutation] = None

    def __post_init__(self):
        super().__post_init__()
        # by default use random swap mutation for all the permitted mutation spread
        if not self.MUTATIONS:
            self.MUTATIONS = [RandomSwapMutation(num_mutations=self.MAX_SPREAD)]

    def validate(self):
        super().validate()
        if (
            self.MUTATIONS
            and sum([mutation.num_mutations for mutation in self.MUTATIONS])
            != self.MAX_SPREAD
        ):
            raise ValueError(
                "The total number of outputted team sets from specified mutations =/= MAX_SPREAD!"
            )
