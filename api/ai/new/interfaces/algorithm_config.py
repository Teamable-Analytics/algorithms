from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Tuple, List

from api.ai.new.priority_algorithm.mutations.random_swap import mutate_random_swap


class AlgorithmConfig(ABC):
    """
    An algorithm config is semantically different from AlgorithmOptions.
    AlgorithmConfig specifies underlying constants and internals that are largely set by developers, not the user.

    i.e. The maximum amount of time an algorithm is allowed to run for is a config choice, not an options choice.
    """

    def __post_init__(self):
        self.validate()

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


@dataclass
class PriorityAlgorithmConfig(AlgorithmConfig):
    MAX_KEEP: int  # nodes
    MAX_SPREAD: int  # nodes
    MAX_ITERATE: int  # iterations
    MAX_TIME: int  # seconds

    """
    Specifies the mutations as a list of [mutation_function, number_team_sets_generated_this_way]
    i.e. if one wants to mutate by "make 3 team sets using random mutation and 5 using local max mutation":
        [
            (random_mutation, 3),
            (local_max_mutation, 5),
        ]
    """
    MUTATIONS: List[Tuple[Callable, int]] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        # by default use random swap mutation for all the permitted mutation spread
        if not self.MUTATIONS:
            self.MUTATIONS = [(mutate_random_swap, self.MAX_SPREAD)]

    def validate(self):
        super().validate()
        if (
            self.MUTATIONS
            and sum([output for _, output in self.MUTATIONS]) != self.MAX_SPREAD
        ):
            raise ValueError(
                "The total number of outputted team sets from specified mutations =/= MAX_SPREAD!"
            )
