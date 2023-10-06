from abc import ABC, abstractmethod


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


class PriorityAlgorithmConfig(AlgorithmConfig):
    def validate(self):
        super().validate()
