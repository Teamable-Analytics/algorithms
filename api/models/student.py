from dataclasses import dataclass, field
from typing import List, Dict

from api.models.enums import Relationship


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

    def to_json(self):
        attributes_json = {}
        for key, value in self.attributes.items():
            attributes_json[str(key)] = value
        return {
            "_id": self._id,
            "name": self.name,
            "attributes": attributes_json,
            "preferences": self.preferences,
        }
