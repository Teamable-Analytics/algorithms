from typing import List, cast

from api.ai.new.interfaces.algorithm import Algorithm
from api.ai.new.interfaces.algorithm_options import PathGaspAlgorithmOptions
from api.models.student.student import Student
from api.models.team_set import TeamSet


class PathGaspAlgorithm(Algorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.algorithm_options: PathGaspAlgorithmOptions = cast(
            PathGaspAlgorithmOptions, self.algorithm_options
        )

    def generate(self, students: List[Student]) -> TeamSet:
        pass
