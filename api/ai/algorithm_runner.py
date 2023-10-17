from typing import List

from api.ai.new.interfaces.algorithm_config import AlgorithmConfig
from api.ai.new.interfaces.algorithm_options import AlgorithmOptions
from api.ai.new.interfaces.team_generation_options import TeamGenerationOptions
from api.ai.new.multiple_round_robin_with_adjusted_winner.multiple_round_robin import (
    MultipleRoundRobinWithAdjustedWinnerAlgorithm,
)
from api.ai.new.priority_algorithm.priority_algorithm import PriorityAlgorithm
from api.ai.new.random_algorithm.random_algorithm import RandomAlgorithm
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
        print("ALGO " + str(self.algorithm))
        return self.algorithm.generate(students)

    @staticmethod
    def get_algorithm_from_type(algorithm_type: AlgorithmType):
        print("ALGO TYPE " + str(algorithm_type))
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

        raise NotImplementedError(
            f"Algorithm type {algorithm_type} is not associated with an algorithm class!"
        )
