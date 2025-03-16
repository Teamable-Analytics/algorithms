from dataclasses import dataclass, field
from typing import List

from algorithms.dataclasses.team import Team


@dataclass
class TeamSet:
    _id: str = None
    name: str = None
    teams: List[Team] = field(default_factory=list)

    @property
    def num_teams(self) -> int:
        return len(self.teams)

    @property
    def id(self) -> int:
        return self._id
