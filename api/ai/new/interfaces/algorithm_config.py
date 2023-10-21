from abc import ABC, abstractmethod
from dataclasses import dataclass


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

    def validate(self):
        super().validate()
