from typing import List, Tuple, Optional, cast

from api.ai.interfaces.algorithm import ChooseAlgorithm
from api.ai.interfaces.algorithm_config import WeightAlgorithmConfig
from api.ai.interfaces.algorithm_options import (
    WeightAlgorithmOptions,
)
from api.ai.utils import generate_with_choose
from api.ai.weight_algorithm.utility import (
    get_requirement_utility,
    get_social_utility,
    get_diversity_utility,
    get_preference_utility,
)
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet

DEFAULT_WEIGHT_ALGORITHM_CONFIG = WeightAlgorithmConfig()


class WeightAlgorithm(ChooseAlgorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.algorithm_options: WeightAlgorithmOptions = cast(
            WeightAlgorithmOptions, self.algorithm_options
        )
        if self.algorithm_config:
            self.algorithm_config: WeightAlgorithmConfig = cast(
                WeightAlgorithmConfig, self.algorithm_config
            )
        else:
            self.algorithm_config = DEFAULT_WEIGHT_ALGORITHM_CONFIG

    def generate(self, students: List[Student]) -> TeamSet:
        return generate_with_choose(self, students, self.teams)

    def choose(
        self, teams: List[Team], students: List[Student]
    ) -> Tuple[Optional[Team], Optional[Student]]:
        """Choose the smallest team and the student that has the highest utility for that team"""
        smallest_team = None
        for team in teams:
            if smallest_team is None or team.size < smallest_team.size:
                smallest_team = team

        if not smallest_team:
            return None, None

        greatest_utility = 0
        greatest_utility_student = None
        for student in students:
            utility = WeightAlgorithm.get_utility(
                self.algorithm_options, smallest_team, student
            )
            if greatest_utility_student is None or utility > greatest_utility:
                greatest_utility = utility
                greatest_utility_student = student

        return smallest_team, greatest_utility_student

    @staticmethod
    def get_utility(
        algorithm_options: WeightAlgorithmOptions, team: Team, student: Student
    ) -> float:
        """
        Get the utility for each of the four weights, requirement/social/diversity/preference.
        Then combine each of the normalized weights. Each utility is modified based on the options.
        """
        if student in team.students:
            return 0

        requirement_utility = (
            get_requirement_utility(team, student)
            * algorithm_options.requirement_weight
        )
        social_utility = (
            get_social_utility(team, [student]) * algorithm_options.social_weight
        )
        diversity_utility = (
            get_diversity_utility(
                team,
                student,
                algorithm_options.attributes_to_diversify,
                algorithm_options.attributes_to_concentrate,
            )
            * algorithm_options.diversity_weight
        )
        preference_utility = (
            get_preference_utility(
                team, student, algorithm_options.max_project_preferences
            )
            * algorithm_options.preference_weight
        )

        return (
            requirement_utility
            + social_utility
            + diversity_utility
            + preference_utility
        )
