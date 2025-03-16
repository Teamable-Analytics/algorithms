from random import randint
from typing import List, Tuple, Optional, cast

from algorithms.ai.interfaces.algorithm import ChooseAlgorithm
from algorithms.ai.interfaces.algorithm_config import RandomAlgorithmConfig
from algorithms.ai.interfaces.algorithm_options import RandomAlgorithmOptions
from algorithms.ai.utils import generate_with_choose
from algorithms.dataclasses.student import Student
from algorithms.dataclasses.team import Team
from algorithms.dataclasses.team_set import TeamSet


class RandomAlgorithm(ChooseAlgorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.algorithm_options: RandomAlgorithmOptions = cast(
            RandomAlgorithmOptions, self.algorithm_options
        )
        if self.algorithm_config:
            self.algorithm_config: RandomAlgorithmConfig = cast(
                RandomAlgorithmConfig, self.algorithm_config
            )
        else:
            self.algorithm_config = RandomAlgorithmConfig()

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
