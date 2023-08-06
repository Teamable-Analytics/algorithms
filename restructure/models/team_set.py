from dataclasses import dataclass, field
from typing import List

from restructure.models.team import Team


@dataclass
class TeamSet:
    _id: int
    name: str = None
    teams: List[Team] = field(default_factory=list)
