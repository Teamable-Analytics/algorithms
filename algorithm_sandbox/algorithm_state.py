import copy
from typing import List

from team_formation.app.team_generator.team import Team


class AlgorithmState:
    """
    This object represents a snapshot of an algorithms run.
    It contains the current team compositions and the stage of the algorithm.
    """

    def __init__(self, teams: List[Team], stage: int = None):
        self.current_team_compositions = copy.deepcopy(teams)
        self.stage = stage
