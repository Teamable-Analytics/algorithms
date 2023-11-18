from typing import Dict, List

from api.ai.interfaces.algorithm_config import (
    AlgorithmConfig,
    RandomAlgorithmConfig,
    WeightAlgorithmConfig,
    SocialAlgorithmConfig,
)
from api.models.enums import AlgorithmType
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.utils.team_calculations import *
from benchmarking.runs.interfaces import Run


class SocialRun(Run):
    metrics: Dict[str, TeamSetMetric] = {
        "Strictly Happy Team (Friend)": AverageSocialSatisfaction(
            metric_function=is_strictly_happy_team_friend,
            name="Strictly Happy Team (Friend)",
        ),
        "Strictly Happy Team (Enemy)": AverageSocialSatisfaction(
            metric_function=is_strictly_happy_team_enemy,
            name="Strictly Happy Team (Enemy)",
        ),
        "Happy Team 1SHP (Friend)": AverageSocialSatisfaction(
            metric_function=is_happy_team_1shp_friend,
            name="Happy Team 1SHP (Friend)",
        ),
        "Happy Team 1SHP (Enemy)": AverageSocialSatisfaction(
            metric_function=is_happy_team_1shp_enemy,
            name="Happy Team 1SHP (Enemy)",
        ),
        "Happy Team 1HP (Friend)": AverageSocialSatisfaction(
            metric_function=is_happy_team_1hp_friend,
            name="Happy Team 1HP (Friend)",
        ),
        "Happy Team 1HP (Enemy)": AverageSocialSatisfaction(
            metric_function=is_happy_team_1hp_enemy,
            name="Happy Team 1HP (Enemy)",
        ),
        "Happy Team All HP (Friend)": AverageSocialSatisfaction(
            metric_function=is_happy_team_allhp_friend,
            name="Happy Team All HP (Friend)",
        ),
        "Happy Team All HP (Enemy)": AverageSocialSatisfaction(
            metric_function=is_happy_team_allhp_enemy,
            name="Happy Team All HP (Enemy)",
        ),
    }

    algorithms: Dict[AlgorithmType, List[AlgorithmConfig]] = {
        AlgorithmType.RANDOM: [RandomAlgorithmConfig()],
        AlgorithmType.WEIGHT: [WeightAlgorithmConfig()],
        AlgorithmType.SOCIAL: [SocialAlgorithmConfig()],
    }

    @staticmethod
    def start(num_trials: int = 10, generate_graphs: bool = False):
        raise NotImplementedError
