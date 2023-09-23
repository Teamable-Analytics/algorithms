from random import randint
from typing import List, Tuple, Optional, cast

from ai.new.interfaces.algorithm import Algorithm, ChooseAlgorithm
from ai.new.interfaces.algorithm_options import RandomAlgorithmOptions
from ai.new.utils import generate_with_choose
from models.student import Student
from models.team import Team
from models.team_set import TeamSet


class RandomAlgorithm(ChooseAlgorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.algorithm_options: RandomAlgorithmOptions = cast(RandomAlgorithmOptions, self.algorithm_options)

    def generate(self, students: List[Student]) -> TeamSet:
        return generate_with_choose(self, students, self.teams)

    def choose(
        self, teams: List[Team], students: List[Student]
    ) -> Tuple[Optional[Team], Optional[Student]]:
        """Choose the smallest team and a random student"""
        smallest_team = None
        for team in teams:
            if smallest_team is None or team.size < smallest_team.size:
                smallest_team = team
        student_size = len(students)

        if not smallest_team or not student_size:
            return None, None

        random_student = students[randint(0, student_size - 1)]

        return smallest_team, random_student
