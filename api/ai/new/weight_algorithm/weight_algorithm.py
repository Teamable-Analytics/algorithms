from typing import List, Tuple, Optional, cast

from api.ai.new.interfaces.algorithm import ChooseAlgorithm
from api.ai.new.interfaces.algorithm_options import WeightAlgorithmOptions
from api.ai.new.utils import generate_with_choose
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet


class WeightAlgorithm(ChooseAlgorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.algorithm_options: WeightAlgorithmOptions = cast(
            WeightAlgorithmOptions, self.algorithm_options
        )

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
