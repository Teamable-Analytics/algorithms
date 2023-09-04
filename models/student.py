from dataclasses import dataclass, field
from typing import List, Dict

from models.enums import Relationship
from models.team import Team


@dataclass
class Student:
    _id: int
    name: str = None
    attributes: Dict[int, List[any]] = field(default_factory=dict)
    relationships: Dict[int, Relationship] = field(default_factory=dict)
    preferences: List[int] = field(default_factory=list)
    team: Team = None

    def get_id(self):
        return self._id
