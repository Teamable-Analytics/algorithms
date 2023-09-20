import json
from dataclasses import dataclass, field
from json import JSONEncoder
from typing import List, Dict

from models.enums import Relationship


@dataclass
class Student:
    _id: int
    name: str = None
    attributes: Dict[int, List[any]] = field(default_factory=dict)
    relationships: Dict[int, Relationship] = field(default_factory=dict)
    preferences: List[int] = field(default_factory=list)
    team: "Team" = None

    @property
    def id(self) -> int:
        return self._id

    def add_team(self, team: "Team"):
        if self.team:
            return False
        self.team = team
        return True


class StudentEncoder(JSONEncoder):
    def default(self, o):
        return {"id": str(o.id), "preferences": str(o.preferences)}
