import copy
from typing import List

from team import Team


class AlgorithmState:
    def __init__(self, teams: List[Team], stage: int = None):
        self.current_team_compositions = copy.deepcopy(teams)
        self.stage = stage
