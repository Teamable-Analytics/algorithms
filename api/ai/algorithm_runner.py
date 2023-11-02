from typing import List

from api.ai.new.interfaces.algorithm_config import (
    AlgorithmConfig,
    RandomAlgorithmConfig,
    WeightAlgorithmConfig,
    SocialAlgorithmConfig,
    PriorityAlgorithmConfig,
)
from api.ai.new.interfaces.algorithm_options import (
    AlgorithmOptions,
    RandomAlgorithmOptions,
    WeightAlgorithmOptions,
    SocialAlgorithmOptions,
    PriorityAlgorithmOptions,
    MultipleRoundRobinAlgorithmOptions,
    RarestFirstAlgorithmOptions,
)
from api.ai.new.interfaces.team_generation_options import TeamGenerationOptions
from api.ai.new.multiple_round_robin_with_adjusted_winner.multiple_round_robin import (
    MultipleRoundRobinWithAdjustedWinnerAlgorithm,
)
from api.ai.new.priority_algorithm.priority_algorithm import PriorityAlgorithm
from api.ai.new.random_algorithm.random_algorithm import RandomAlgorithm
from api.ai.new.rarest_first_algorithm.rarest_first_algorithm import (
    RarestFirstAlgorithm,
)
from api.ai.new.social_algorithm.social_algorithm import SocialAlgorithm
from api.ai.new.weight_algorithm.weight_algorithm import WeightAlgorithm
from api.models.enums import AlgorithmType
from api.models.student import Student
from api.models.team_set import TeamSet


class AlgorithmRunner:
    def __init__(
        self,
        algorithm_type: AlgorithmType,
        team_generation_options: TeamGenerationOptions,
        algorithm_options: AlgorithmOptions,
        algorithm_config: AlgorithmConfig = None,
    ):
        self.algorithm_cls = AlgorithmRunner.get_algorithm_from_type(algorithm_type)
        self.team_generation_options = team_generation_options

        self.algorithm = self.algorithm_cls(
            team_generation_options=team_generation_options,
            algorithm_options=algorithm_options,
            algorithm_config=algorithm_config,
        )

    def generate(self, students: List[Student]) -> TeamSet:
        return self.algorithm.generate(students)

    @staticmethod
    def get_algorithm_from_type(algorithm_type: AlgorithmType):
        if algorithm_type == AlgorithmType.RANDOM:
            return RandomAlgorithm
        if algorithm_type == AlgorithmType.WEIGHT:
            return WeightAlgorithm
        if algorithm_type == AlgorithmType.SOCIAL:
            return SocialAlgorithm
        if algorithm_type == AlgorithmType.PRIORITY:
            return PriorityAlgorithm
        # todo: fix to use old priority way
        if algorithm_type == AlgorithmType.PRIORITY_NEW:
            return PriorityAlgorithm
        if algorithm_type == AlgorithmType.MRR:
            return MultipleRoundRobinWithAdjustedWinnerAlgorithm
        if algorithm_type == AlgorithmType.RAREST_FIRST:
            return RarestFirstAlgorithm

        raise NotImplementedError(
            f"Algorithm type {algorithm_type} is not associated with an algorithm class!"
        )

    @staticmethod
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
        if algorithm_type == AlgorithmType.RAREST_FIRST:
            return RarestFirstAlgorithmOptions

        raise NotImplementedError(
            f"Algorithm type {algorithm_type} is not associated with an algorithm options class!"
        )

    @staticmethod
    def get_algorithm_config_class(algorithm_type: AlgorithmType):
        if algorithm_type == AlgorithmType.RANDOM:
            return RandomAlgorithmConfig
        if algorithm_type == AlgorithmType.WEIGHT:
            return WeightAlgorithmConfig
        if algorithm_type == AlgorithmType.SOCIAL:
            return SocialAlgorithmConfig
        if algorithm_type == AlgorithmType.PRIORITY:
            return PriorityAlgorithmConfig
        if algorithm_type == AlgorithmType.PRIORITY_NEW:
            return PriorityAlgorithmConfig
        if algorithm_type == AlgorithmType.MRR:
            return None
        if algorithm_type == AlgorithmType.RAREST_FIRST:
            return None

        raise NotImplementedError(
            f"Algorithm type {algorithm_type} is not associated with an algorithm config class!"
        )
