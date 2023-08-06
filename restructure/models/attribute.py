from dataclasses import dataclass, field
from typing import List


@dataclass
class Attribute:
    _id: int
    possible_values: List[int] = None


@dataclass
class AttributeValue:
    value: List[any] = field(default_factory=list)
