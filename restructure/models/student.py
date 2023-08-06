from dataclasses import dataclass, field
from typing import List, Dict

from restructure.models.attribute import AttributeValue
from restructure.models.enums import Relationship


@dataclass
class Student:
    _id: int
    name: str = None
    attributes: Dict[int, AttributeValue] = field(default_factory=dict)
    relationships: Dict[int, Relationship] = field(default_factory=dict)
    preferences: List[int] = field(default_factory=list)
