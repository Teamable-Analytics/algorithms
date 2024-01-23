from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Tuple, List

from api.models.student import Student
from api.models.team import TeamShell


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


@dataclass
class PriorityAlgorithmConfig(AlgorithmConfig):
    MAX_KEEP: int = 15  # nodes
    MAX_SPREAD: int = 30  # nodes
    MAX_ITERATE: int = 30  # iterations
    MAX_TIME: int = 10000000  # seconds

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
            from api.ai.priority_algorithm.mutations.random_swap import (
                mutate_random_swap,
            )

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


class MultipleRoundRobinAlgorithmConfig(AlgorithmConfig):
    utility_function: Callable[[Student, TeamShell], float]

    def __init__(self, utility_function: Callable[[Student, TeamShell], float]):
        super().__init__()
        self.utility_function = utility_function

    def validate(self):
        super().validate()


class DoubleRoundRobinAlgorithmConfig(AlgorithmConfig):
    utility_function: Callable[[Student, TeamShell], float]

    def __init__(self, utility_function: Callable[[Student, TeamShell], float]):
        super().__init__()
        self.utility_function = utility_function

    def validate(self):
        super().validate()


class GeneralizedEnvyGraphAlgorithmConfig(AlgorithmConfig):
    utility_function: Callable[[Student, TeamShell], float]

    def __init__(self, utility_function: Callable[[Student, TeamShell], float]):
        super().__init__()
        self.utility_function = utility_function

    def validate(self):
        super().validate()


class GroupMatcherAlgorithmConfig(AlgorithmConfig):
    csv_input_path: str
    group_matcher_run_path: str

    def __init__(self, csv_output_path: str, group_matcher_run_path: str):
        super().__init__()
        self.csv_input_path = csv_output_path
        self.group_matcher_run_path = group_matcher_run_path

    def validate(self):
        super().validate()
