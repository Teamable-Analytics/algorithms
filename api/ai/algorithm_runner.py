from typing import List, TYPE_CHECKING

from api.ai.external_algorithms.group_matcher_algorithm.group_matcher_algorithm import (
    GroupMatcherAlgorithm,
)
from api.ai.geg_algorithm.geg_algorithm import GeneralizedEnvyGraphAlgorithm
from api.ai.interfaces.algorithm_config import (
    AlgorithmConfig,
    RandomAlgorithmConfig,
    WeightAlgorithmConfig,
    SocialAlgorithmConfig,
    PriorityAlgorithmConfig,
    GroupMatcherAlgorithmConfig,
)
from api.ai.interfaces.algorithm_options import (
    RandomAlgorithmOptions,
    WeightAlgorithmOptions,
    SocialAlgorithmOptions,
    PriorityAlgorithmOptions,
    MultipleRoundRobinAlgorithmOptions,
    GeneralizedEnvyGraphAlgorithmOptions,
    DoubleRoundRobinAlgorithmOptions,
    GroupMatcherAlgorithmOptions,
)
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.ai.multiple_round_robin_with_adjusted_winner_algorithm.mrr_algorithm import (
    MultipleRoundRobinWithAdjustedWinnerAlgorithm,
)
from api.ai.priority_algorithm.priority_algorithm import PriorityAlgorithm
from api.ai.random_algorithm.random_algorithm import RandomAlgorithm
from api.ai.social_algorithm.social_algorithm import SocialAlgorithm
from api.ai.weight_algorithm.weight_algorithm import WeightAlgorithm
from api.ai.double_round_robin_algorithm.double_round_robin_algorithm import (
    DoubleRoundRobinAlgorithm,
)
from api.dataclasses.enums import AlgorithmType
from api.dataclasses.student import Student
from api.dataclasses.team_set import TeamSet

if TYPE_CHECKING:
    from api.ai.interfaces.algorithm_options import AlgorithmOptions


class AlgorithmRunner:
    def __init__(
        self,
        algorithm_type: AlgorithmType,
        team_generation_options: TeamGenerationOptions,
        algorithm_options: "AlgorithmOptions",
        algorithm_config: AlgorithmConfig = None,
    ):
        self.algorithm_cls = AlgorithmRunner.get_algorithm_from_type(algorithm_type)
        self.team_generation_options = team_generation_options
        self.algorithm_options = algorithm_options
        self.algorithm_config = algorithm_config

    def generate(self, students: List[Student]) -> TeamSet:
        # the algorithm classes internally track generated teams, so a new instance of the
        #   algorithm class MUST be created to run a new generation without side effects
        algorithm = self.algorithm_cls(
            team_generation_options=self.team_generation_options,
            algorithm_options=self.algorithm_options,
            algorithm_config=self.algorithm_config,
        )

        algorithm.prepare(students)

        return algorithm.generate(students)

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
        if algorithm_type == AlgorithmType.MRR:
            return MultipleRoundRobinWithAdjustedWinnerAlgorithm
        if algorithm_type == AlgorithmType.GEG:
            return GeneralizedEnvyGraphAlgorithm
        if algorithm_type == AlgorithmType.DRR:
            return DoubleRoundRobinAlgorithm
        if algorithm_type == AlgorithmType.GROUP_MATCHER:
            return GroupMatcherAlgorithm

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
        if algorithm_type == AlgorithmType.MRR:
            return MultipleRoundRobinAlgorithmOptions
        if algorithm_type == AlgorithmType.GEG:
            return GeneralizedEnvyGraphAlgorithmOptions
        if algorithm_type == AlgorithmType.DRR:
            return DoubleRoundRobinAlgorithmOptions
        if algorithm_type == AlgorithmType.GROUP_MATCHER:
            return GroupMatcherAlgorithmOptions

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
        if algorithm_type == AlgorithmType.MRR:
            return None
        if algorithm_type == AlgorithmType.GEG:
            return None
        if algorithm_type == AlgorithmType.DRR:
            return None
        if algorithm_type == AlgorithmType.GROUP_MATCHER:
            return GroupMatcherAlgorithmConfig

        raise NotImplementedError(
            f"Algorithm type {algorithm_type} is not associated with an algorithm config class!"
        )
