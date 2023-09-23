from random import randint
from typing import List, Tuple, Optional, cast

from ai.new.interfaces.algorithm import ChooseAlgorithm
from ai.new.interfaces.algorithm_options import WeightAlgorithmOptions
from ai.new.utils import generate_with_choose
from models.student import Student
from models.team import Team
from models.team_set import TeamSet


class WeightAlgorithm(ChooseAlgorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.algorithm_options: WeightAlgorithmOptions = cast(WeightAlgorithmOptions, self.algorithm_options)

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
            utility = self._get_utility(smallest_team, student)
            if greatest_utility_student is None or utility > greatest_utility:
                greatest_utility = utility
                greatest_utility_student = student

        return smallest_team, greatest_utility_student

    def _get_utility(self, team: Team, student: Student):
        """
        Get the utility for each of the four weights, requirement/social/diversity/preference.
        Then combine each of the normalized weights. Each utility is modified based on the options.
        """
        # todo: finish
        return 1

        # if student in team.students:
        #     return 0
        #
        # requirement_utility = (
        #     get_requirement_utility(team, student) * self.options.requirement_weight
        # )
        # social_utility = (
        #     get_social_utility(team, [student]) * self.options.social_weight
        # )
        # diversity_utility = (
        #     get_diversity_utility(
        #         team,
        #         student,
        #         self.options.diversify_options,
        #         self.options.concentrate_options,
        #     )
        #     * self.options.diversity_weight
        # )
        # preference_utility = (
        #     get_preference_utility(team, student, self.options.max_project_preferences)
        #     * self.options.preference_weight
        # )
        #
        # return (
        #     requirement_utility
        #     + social_utility
        #     + diversity_utility
        #     + preference_utility
        # )
