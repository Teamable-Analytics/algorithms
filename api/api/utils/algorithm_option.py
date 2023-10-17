from api.ai.new.interfaces.algorithm_options import (
    RandomAlgorithmOptions,
    WeightAlgorithmOptions,
    SocialAlgorithmOptions,
    PriorityAlgorithmOptions,
    MultipleRoundRobinAlgorithmOptions,
)
from api.models.enums import AlgorithmType


def get_algorithm_option_class(algorithm_type: AlgorithmType):
    if algorithm_type == AlgorithmType.RANDOM:
        return RandomAlgorithmOptions
    if algorithm_type == AlgorithmType.WEIGHT:
        return WeightAlgorithmOptions
    if algorithm_type == AlgorithmType.SOCIAL:
        return SocialAlgorithmOptions
    if algorithm_type == AlgorithmType.PRIORITY:
        return PriorityAlgorithmOptions
    if algorithm_type == AlgorithmType.PRIORITY_NEW:
        return PriorityAlgorithmOptions
    if algorithm_type == AlgorithmType.MRR:
        return MultipleRoundRobinAlgorithmOptions

    raise NotImplementedError(
        f"Algorithm type {algorithm_type} is not associated with an algorithm class!"
    )
